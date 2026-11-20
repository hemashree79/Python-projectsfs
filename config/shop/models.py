from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 1) if avg is not None else None

    @property
    def review_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} ({self.rating}/5) by {self.user.username}"


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(90)]
    )
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"


class GroupDrop(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="group_drop")
    tier1_min_buyers = models.PositiveIntegerField(default=3)
    tier1_price = models.DecimalField(max_digits=10, decimal_places=2)
    tier2_min_buyers = models.PositiveIntegerField(default=5)
    tier2_price = models.DecimalField(max_digits=10, decimal_places=2)
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    @property
    def is_open(self):
        return self.is_active and timezone.now() < self.ends_at

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def current_price(self):
        count = self.participant_count
        if count >= self.tier2_min_buyers:
            return self.tier2_price
        if count >= self.tier1_min_buyers:
            return self.tier1_price
        return self.product.price

    @property
    def current_tier_label(self):
        count = self.participant_count
        if count >= self.tier2_min_buyers:
            return "Tier 3 (Max Drop Unlocked!)"
        if count >= self.tier1_min_buyers:
            return "Tier 2 (Group Discount Unlocked!)"
        return "Tier 1 (Standard Price)"

    @property
    def next_tier_info(self):
        count = self.participant_count
        if count < self.tier1_min_buyers:
            needed = self.tier1_min_buyers - count
            return f"{needed} more buyer{'s' if needed != 1 else ''} needed to drop price to ₹{self.tier1_price}"
        if count < self.tier2_min_buyers:
            needed = self.tier2_min_buyers - count
            return f"{needed} more buyer{'s' if needed != 1 else ''} needed to drop price to ₹{self.tier2_price}"
        return "Lowest group price unlocked for everyone!"

    @property
    def progress_percent(self):
        if self.tier2_min_buyers == 0:
            return 100
        return min(100, int((self.participant_count / self.tier2_min_buyers) * 100))

    def __str__(self):
        return f"Drop Pool: {self.product.name} ({self.participant_count} joined)"


class DropParticipant(models.Model):
    drop = models.ForeignKey(GroupDrop, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="drop_joins")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("drop", "user")
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.username} in {self.drop.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("upi", "UPI (GPay / PhonePe / Paytm)"),
        ("card", "Credit / Debit Card"),
        ("netbanking", "Net Banking"),
        ("cod", "Cash on Delivery (COD)"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pay on Delivery"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    user_order_number = models.PositiveIntegerField(null=True, blank=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="upi")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="paid")
    payment_detail = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=40, blank=True)
    coupon_code = models.CharField(max_length=30, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_number(self):
        return self.user_order_number or self.id

    @property
    def subtotal_amount(self):
        return self.total_amount + self.discount_amount

    def __str__(self):
        return f"Order #{self.display_number} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
