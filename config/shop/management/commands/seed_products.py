from decimal import Decimal
from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = "Seeds sample categories and products without duplicates."

    def handle(self, *args, **options):
        catalog = [
            {
                "category": "Electronics & Peripherals",
                "name": "Noise-Cancelling Wireless Headphones",
                "description": "Over-ear Bluetooth 5.3 headphones with 40-hour battery life and deep bass.",
                "price": Decimal("4999.00"),
                "stock": 6,
            },
            {
                "category": "Electronics & Peripherals",
                "name": "27-Inch 4K IPS Monitor",
                "description": "Ultra-thin bezel display with USB-C connectivity and height-adjustable stand.",
                "price": Decimal("22499.00"),
                "stock": 4,
            },
            {
                "category": "Electronics & Peripherals",
                "name": "Wireless Gaming Mouse",
                "description": "Lightweight 65g optical mouse with customizable DPI and braided USB-C cable.",
                "price": Decimal("2199.00"),
                "stock": 10,
            },
            {
                "category": "Desk & Workspace",
                "name": "LED Desk Lamp with Wireless Charger",
                "description": "Dimmable eye-care study lamp with 3 color modes and built-in 15W Qi charging pad.",
                "price": Decimal("1599.00"),
                "stock": 7,
            },
            {
                "category": "Desk & Workspace",
                "name": "Felt Desk Mat (Large)",
                "description": "Anti-slip wool-blend desk pad for keyboard and mouse protection (90cm x 40cm).",
                "price": Decimal("799.00"),
                "stock": 12,
            },
            {
                "category": "Desk & Workspace",
                "name": "Dual Monitor Riser Shelf",
                "description": "Solid bamboo desk organizer with storage slots for notebooks and accessories.",
                "price": Decimal("1850.00"),
                "stock": 5,
            },
            {
                "category": "Books & Stationery",
                "name": "Clean Code (Paperback)",
                "description": "Handbook of agile software craftsmanship and readable programming practices.",
                "price": Decimal("649.00"),
                "stock": 9,
            },
            {
                "category": "Books & Stationery",
                "name": "Dotted Hardcover Notebook (A5)",
                "description": "200-page 120gsm fountain-pen-friendly journal with lay-flat binding.",
                "price": Decimal("399.00"),
                "stock": 15,
            },
            {
                "category": "Lifestyle & Drinkware",
                "name": "Insulated Stainless Steel Tumbler (750ml)",
                "description": "Double-wall vacuum flask that keeps beverages cold for 24 hours or hot for 12 hours.",
                "price": Decimal("899.00"),
                "stock": 11,
            },
            {
                "category": "Lifestyle & Drinkware",
                "name": "Minimalist Laptop Backpack (15.6\")",
                "description": "Water-resistant commuter backpack with padded laptop sleeve and anti-theft pocket.",
                "price": Decimal("1799.00"),
                "stock": 8,
            },
        ]

        for item in catalog:
            cat_obj, _ = Category.objects.get_or_create(name=item["category"])
            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults={
                    "category": cat_obj,
                    "description": item["description"],
                    "price": item["price"],
                    "stock": item["stock"],
                    "is_available": True,
                },
            )
            if not created and product.category is None:
                product.category = cat_obj
                product.save()
            status = "Created" if created else "Updated/Exists"
            self.stdout.write(f"{status}: {product.name} [{cat_obj.name}]")

        # Assign categories to the original 3 seeded items if they exist
        elec, _ = Category.objects.get_or_create(name="Electronics & Peripherals")
        desk, _ = Category.objects.get_or_create(name="Desk & Workspace")
        Product.objects.filter(name__in=["Wireless Mechanical Keyboard", "USB-C Multiport Hub"]).update(category=elec)
        Product.objects.filter(name="Ergonomic Laptop Stand").update(category=desk)
