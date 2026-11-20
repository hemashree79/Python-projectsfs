from decimal import Decimal
from .models import DropParticipant, Product


def get_effective_unit_price(request, product):
    if request.user.is_authenticated and hasattr(product, "group_drop"):
        drop = product.group_drop
        if drop.is_open and DropParticipant.objects.filter(drop=drop, user=request.user).exists():
            return drop.current_price
    return product.price


def get_cart(request):
    cart = request.session.get("shopping_cart", {})
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.select_related("group_drop").filter(id__in=product_ids, is_available=True)
    product_map = {p.id: p for p in products}

    items = []
    total = Decimal("0.00")

    for pid_str, quantity in list(cart.items()):
        product = product_map.get(int(pid_str))
        if not product or product.stock <= 0:
            del cart[pid_str]
            request.session.modified = True
            continue

        valid_qty = min(quantity, product.stock)
        if valid_qty != quantity:
            cart[pid_str] = valid_qty
            request.session.modified = True

        unit_price = get_effective_unit_price(request, product)
        line_total = unit_price * valid_qty
        total += line_total
        items.append({
            "product": product,
            "quantity": valid_qty,
            "unit_price": unit_price,
            "is_drop_price": unit_price < product.price,
            "line_total": line_total,
        })

    return items, total
