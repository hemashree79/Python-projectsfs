from django import forms
from .models import Order, Review


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial="upi",
    )
    upi_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "yourname@okaxis / yourname@ybl"}),
    )
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={"placeholder": "4532 •••• •••• 8890"}),
    )
    card_expiry = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={"placeholder": "MM/YY"}),
    )
    card_cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.PasswordInput(attrs={"placeholder": "•••"}),
    )
    bank_name = forms.ChoiceField(
        required=False,
        choices=[
            ("HDFC Bank", "HDFC Bank"),
            ("ICICI Bank", "ICICI Bank"),
            ("State Bank of India", "State Bank of India"),
            ("Axis Bank", "Axis Bank"),
            ("Kotak Mahindra Bank", "Kotak Mahindra Bank"),
        ],
    )

    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "address", "payment_method"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full Name", "required": True}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "required": True}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 98765 43210", "required": True}),
            "address": forms.Textarea(attrs={"rows": 3, "placeholder": "Full delivery address", "required": True}),
        }

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("payment_method")

        if method == "upi":
            upi = (cleaned.get("upi_id") or "").strip()
            if not upi or "@" not in upi:
                self.add_error("upi_id", "Enter a valid UPI ID (e.g., name@okicici).")
            else:
                cleaned["resolved_detail"] = f"UPI: {upi}"

        elif method == "card":
            digits = "".join(ch for ch in (cleaned.get("card_number") or "") if ch.isdigit())
            expiry = (cleaned.get("card_expiry") or "").strip()
            cvv = (cleaned.get("card_cvv") or "").strip()
            if len(digits) < 12:
                self.add_error("card_number", "Enter a valid 12–16 digit card number.")
            if not expiry or "/" not in expiry:
                self.add_error("card_expiry", "Enter expiry as MM/YY.")
            if len(cvv) < 3 or not cvv.isdigit():
                self.add_error("card_cvv", "Enter a valid 3 or 4 digit CVV.")
            if digits:
                cleaned["resolved_detail"] = f"Card ending •••• {digits[-4:]}"

        elif method == "netbanking":
            bank = cleaned.get("bank_name") or "HDFC Bank"
            cleaned["resolved_detail"] = f"Net Banking: {bank}"

        elif method == "cod":
            cleaned["resolved_detail"] = "Cash on Delivery"

        return cleaned


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, "★★★★★ (5 - Excellent)"),
        (4, "★★★★☆ (4 - Good)"),
        (3, "★★★☆☆ (3 - Average)"),
        (2, "★★☆☆☆ (2 - Poor)"),
        (1, "★☆☆☆☆ (1 - Terrible)"),
    ]

    rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Share your experience with this product...",
            }),
        }
