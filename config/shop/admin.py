from django.contrib import admin
from .models import Category, Coupon, DropParticipant, GroupDrop, Order, OrderItem, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "comment")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "min_order_amount", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code",)


class DropParticipantInline(admin.TabularInline):
    model = DropParticipant
    extra = 0


@admin.register(GroupDrop)
class GroupDropAdmin(admin.ModelAdmin):
    list_display = ("product", "participant_count", "current_price", "tier1_price", "tier2_price", "ends_at", "is_active")
    list_filter = ("is_active",)
    inlines = [DropParticipantInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ("product",)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_order_number", "full_name", "coupon_code", "discount_amount", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "id")
    inlines = [OrderItemInline]
