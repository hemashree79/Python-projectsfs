from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .cart import get_cart, get_effective_unit_price
from .forms import CheckoutForm, ReviewForm
from .models import (
    Category,
    Coupon,
    DropParticipant,
    GroupDrop,
    Order,
    OrderItem,
    Product,
    Review,
    Wishlist,
)


def _get_wishlist_ids(request):
    if request.user.is_authenticated:
        return set(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True))
    return set()


def _get_cart_pricing(request):
    items, subtotal = get_cart(request)
    coupon_code = request.session.get("coupon_code", "")
    coupon = None
    discount = Decimal("0.00")

    if coupon_code and subtotal > 0:
        coupon = Coupon.objects.filter(code__iexact=coupon_code, is_active=True).first()
        if coupon and subtotal >= coupon.min_order_amount:
            discount = (subtotal * Decimal(coupon.discount_percent) / Decimal("100")).quantize(Decimal("0.01"))
        else:
            request.session.pop("coupon_code", None)
            coupon = None

    final_total = max(Decimal("0.00"), subtotal - discount)
    return items, subtotal, coupon, discount, final_total


def product_list(request):
    products = (
        Product.objects.filter(is_available=True, stock__gt=0)
        .select_related("category", "group_drop")
        .annotate(avg_rating=Avg("reviews__rating"), num_reviews=Count("reviews"))
    )
    categories = Category.objects.all()

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    sort = request.GET.get("sort", "newest")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "rating":
        products = products.order_by("-avg_rating", "-num_reviews", "-created_at")
    else:
        products = products.order_by("-created_at")

    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "shop/product_list.html", {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "selected_sort": sort,
        "compare_ids": request.session.get("compare_ids", []),
        "wishlist_ids": _get_wishlist_ids(request),
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category", "group_drop"), id=product_id, is_available=True)
    reviews = product.reviews.select_related("user")
    existing_review = Review.objects.filter(product=product, user=request.user).first() if request.user.is_authenticated else None

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to leave a review.")
            return redirect("shop:login")
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been saved!")
            return redirect("shop:product_detail", product_id=product.id)
    else:
        form = ReviewForm(instance=existing_review)

    related_products = Product.objects.none()
    if product.category:
        related_products = (
            Product.objects.filter(category=product.category, is_available=True, stock__gt=0)
            .exclude(id=product.id)
            .annotate(avg_rating=Avg("reviews__rating"), num_reviews=Count("reviews"))[:4]
        )

    recent_ids = request.session.get("recently_viewed", [])
    other_recent_ids = [pid for pid in recent_ids if pid != product.id][:4]
    recent_map = Product.objects.filter(id__in=other_recent_ids, is_available=True).in_bulk()
    recently_viewed = [recent_map[pid] for pid in other_recent_ids if pid in recent_map]
    request.session["recently_viewed"] = ([product.id] + [pid for pid in recent_ids if pid != product.id])[:5]

    joined_drop = False
    if request.user.is_authenticated and hasattr(product, "group_drop"):
        joined_drop = DropParticipant.objects.filter(drop=product.group_drop, user=request.user).exists()

    return render(request, "shop/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "form": form,
        "existing_review": existing_review,
        "compare_ids": request.session.get("compare_ids", []),
        "wishlist_ids": _get_wishlist_ids(request),
        "related_products": related_products,
        "recently_viewed": recently_viewed,
        "joined_drop": joined_drop,
    })


def drop_pools(request):
    drops = (
        GroupDrop.objects.filter(is_active=True, ends_at__gt=timezone.now(), product__is_available=True, product__stock__gt=0)
        .select_related("product", "product__category")
        .prefetch_related("participants__user")
        .order_by("ends_at")
    )
    joined_drop_ids = set()
    if request.user.is_authenticated:
        joined_drop_ids = set(
            DropParticipant.objects.filter(user=request.user, drop__in=drops).values_list("drop_id", flat=True)
        )
    return render(request, "shop/drop_pools.html", {"drops": drops, "joined_drop_ids": joined_drop_ids})


@login_required
@require_POST
def drop_toggle(request, drop_id):
    drop = get_object_or_404(GroupDrop, id=drop_id)
    if not drop.is_open:
        messages.error(request, "This Group-Buy Drop Pool has already ended.")
        return redirect("shop:drop_pools")
    participant, created = DropParticipant.objects.get_or_create(drop=drop, user=request.user)
    if created:
        messages.success(request, f"You joined the {drop.product.name} Drop Pool! Current group price: ₹{drop.current_price}.")
    else:
        participant.delete()
        messages.info(request, f"You left the {drop.product.name} Drop Pool.")
    return redirect(request.META.get("HTTP_REFERER", "shop:drop_pools"))


def bundle_builder(request):
    available_products = Product.objects.filter(is_available=True, stock__gt=0).order_by("price")
    categories = Category.objects.prefetch_related(
        Prefetch("products", queryset=available_products, to_attr="available_products")
    )
    if request.method == "POST":
        selected_products, selected_categories = [], set()
        for cat in categories:
            prod_id = request.POST.get(f"cat_{cat.id}")
            if prod_id:
                product = Product.objects.filter(id=prod_id, category=cat, is_available=True, stock__gt=0).first()
                if product:
                    selected_products.append(product)
                    selected_categories.add(cat.id)
        if len(selected_categories) < 3:
            messages.warning(request, "Pick at least 1 item from 3 different categories to unlock the 15% Bundle Discount!")
            return redirect("shop:bundle_builder")
        cart = request.session.get("shopping_cart", {})
        for product in selected_products:
            key = str(product.id)
            cart[key] = min(product.stock, cart.get(key, 0) + 1)
        request.session["shopping_cart"] = cart
        request.session["coupon_code"] = "BUNDLE15"
        messages.success(request, f"Custom {len(selected_products)}-item kit added to cart with 15% Bundle Discount (BUNDLE15)!")
        return redirect("shop:cart_detail")
    return render(request, "shop/bundle_builder.html", {"categories": categories})


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"Saved {product.name} to your wishlist.")
    else:
        item.delete()
        messages.info(request, f"Removed {product.name} from your wishlist.")
    return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user, product__is_available=True).select_related("product", "product__category")
    return render(request, "shop/wishlist.html", {"wishlist_items": wishlist_items})


def _add_product_to_session_cart(request, product):
    cart = request.session.get("shopping_cart", {})
    key = str(product.id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
    new_qty = cart.get(key, 0) + max(1, quantity)
    if new_qty > product.stock:
        cart[key] = product.stock
        messages.warning(request, f"Only {product.stock} available for {product.name}.")
    else:
        cart[key] = new_qty
    request.session["shopping_cart"] = cart


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    _add_product_to_session_cart(request, product)
    return redirect("shop:cart_detail")


@require_POST
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    _add_product_to_session_cart(request, product)
    return redirect("shop:checkout")


@require_POST
def compare_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    compare_ids = request.session.get("compare_ids", [])
    if product.id in compare_ids:
        compare_ids.remove(product.id)
        messages.info(request, f"Removed {product.name} from comparison.")
    elif len(compare_ids) >= 4:
        messages.warning(request, "You can compare up to 4 products at a time.")
    else:
        compare_ids.append(product.id)
        messages.success(request, f"Added {product.name} to comparison.")
    request.session["compare_ids"] = compare_ids
    return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))


def compare_view(request):
    compare_ids = request.session.get("compare_ids", [])
    products = Product.objects.filter(id__in=compare_ids, is_available=True).annotate(avg_rating=Avg("reviews__rating"), num_reviews=Count("reviews"))
    return render(request, "shop/compare.html", {"products": products})


@require_POST
def compare_clear(request):
    request.session["compare_ids"] = []
    return redirect("shop:product_list")


@require_POST
def apply_coupon(request):
    code = request.POST.get("code", "").strip().upper()
    _, subtotal = get_cart(request)
    coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
    if not coupon:
        messages.error(request, "Invalid or expired promo code.")
    elif subtotal < coupon.min_order_amount:
        messages.warning(request, f"Code {coupon.code} requires a minimum order of ₹{coupon.min_order_amount}.")
    else:
        request.session["coupon_code"] = coupon.code
        messages.success(request, f"Promo code {coupon.code} ({coupon.discount_percent}% off) applied!")
    return redirect("shop:cart_detail")


@require_POST
def remove_coupon(request):
    request.session.pop("coupon_code", None)
    messages.info(request, "Promo code removed.")
    return redirect("shop:cart_detail")


def cart_detail(request):
    items, subtotal, coupon, discount, final_total = _get_cart_pricing(request)
    return render(request, "shop/cart_detail.html", {"items": items, "subtotal": subtotal, "coupon": coupon, "discount": discount, "total": final_total})


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get("shopping_cart", {})
    key = str(product.id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
    if quantity <= 0:
        cart.pop(key, None)
    elif quantity > product.stock:
        cart[key] = product.stock
        messages.warning(request, f"Adjusted quantity to maximum available ({product.stock}).")
    else:
        cart[key] = quantity
    request.session["shopping_cart"] = cart
    return redirect("shop:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = request.session.get("shopping_cart", {})
    cart.pop(str(product_id), None)
    request.session["shopping_cart"] = cart
    return redirect("shop:cart_detail")


def checkout(request):
    items, subtotal, coupon, discount, final_total = _get_cart_pricing(request)
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("shop:product_list")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                    order.user_order_number = Order.objects.filter(user=request.user).count() + 1
                if coupon:
                    order.coupon_code = coupon.code
                    order.discount_amount = discount
                order.total_amount = final_total
                order.save()
                for item in items:
                    product = Product.objects.select_for_update().get(id=item["product"].id)
                    if item["quantity"] > product.stock:
                        messages.error(request, f"Not enough stock for {product.name}.")
                        transaction.set_rollback(True)
                        return redirect("shop:cart_detail")
                    OrderItem.objects.create(order=order, product=product, price=get_effective_unit_price(request, product), quantity=item["quantity"])
                    product.stock -= item["quantity"]
                    if product.stock == 0:
                        product.is_available = False
                    product.save()
            request.session["shopping_cart"] = {}
            request.session.pop("coupon_code", None)
            return redirect("shop:order_success", order_id=order.id)
    else:
        initial = {"full_name": request.user.get_full_name() or request.user.username, "email": request.user.email} if request.user.is_authenticated else {}
        form = CheckoutForm(initial=initial)
    return render(request, "shop/checkout.html", {"form": form, "items": items, "subtotal": subtotal, "coupon": coupon, "discount": discount, "total": final_total})


def order_success(request, order_id):
    return render(request, "shop/order_success.html", {"order": get_object_or_404(Order, id=order_id)})


def register(request):
    if request.user.is_authenticated:
        return redirect("shop:product_list")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect("shop:product_list")
    else:
        form = UserCreationForm()
    return render(request, "shop/register.html", {"form": form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product").order_by("-created_at")
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ("pending", "confirmed"):
        messages.error(request, f"Order #{order.display_number} cannot be cancelled ({order.get_status_display()}).")
        return redirect("shop:order_history")
    with transaction.atomic():
        for item in order.items.select_related("product"):
            product = Product.objects.select_for_update().get(id=item.product.id)
            product.stock += item.quantity
            product.is_available = True
            product.save()
        order.status = "cancelled"
        order.save()
    messages.success(request, f"Order #{order.display_number} has been cancelled and product stock was restored.")
    return redirect("shop:order_history")


@login_required
def order_invoice(request, order_id):
    return render(request, "shop/order_invoice.html", {"order": get_object_or_404(Order, id=order_id, user=request.user)})


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum


@staff_member_required
def owner_dashboard(request):
    valid_orders = Order.objects.exclude(status="cancelled")
    total_revenue = valid_orders.aggregate(rev=Sum("total_amount"))["rev"] or Decimal("0.00")
    total_orders = valid_orders.count()
    cancelled_orders = Order.objects.filter(status="cancelled").count()
    low_stock_products = Product.objects.filter(stock__lte=3).order_by("stock")
    top_products = (
        OrderItem.objects.exclude(order__status="cancelled")
        .values("product__name")
        .annotate(units_sold=Sum("quantity"))
        .order_by("-units_sold")[:5]
    )
    active_drops = GroupDrop.objects.filter(is_active=True, ends_at__gt=timezone.now()).select_related("product")
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:6]

    return render(request, "shop/owner_dashboard.html", {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "cancelled_orders": cancelled_orders,
        "low_stock_products": low_stock_products,
        "top_products": top_products,
        "active_drops": active_drops,
        "recent_orders": recent_orders,
    })
