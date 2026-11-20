from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("drops/", views.drop_pools, name="drop_pools"),
    path("drops/toggle/<int:drop_id>/", views.drop_toggle, name="drop_toggle"),
    path("bundle-builder/", views.bundle_builder, name="bundle_builder"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("compare/", views.compare_view, name="compare_view"),
    path("compare/toggle/<int:product_id>/", views.compare_toggle, name="compare_toggle"),
    path("compare/clear/", views.compare_clear, name="compare_clear"),
    path("wishlist/", views.wishlist_view, name="wishlist_view"),
    path("wishlist/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/coupon/apply/", views.apply_coupon, name="apply_coupon"),
    path("cart/coupon/remove/", views.remove_coupon, name="remove_coupon"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("my-orders/", views.order_history, name="order_history"),
    path("my-orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("my-orders/<int:order_id>/invoice/", views.order_invoice, name="order_invoice"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="shop/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
