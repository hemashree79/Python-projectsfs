from decimal import Decimal
from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = "Seeds additional products and categories without duplicates."

    def handle(self, *args, **options):
        more_products = [
            {
                "category": "Electronics & Peripherals",
                "name": "1080p Autofocus Webcam",
                "description": "Full HD webcam with dual noise-reducing microphones and privacy shutter.",
                "price": Decimal("2499.00"),
                "stock": 7,
            },
            {
                "category": "Electronics & Peripherals",
                "name": "1TB Portable NVMe SSD",
                "description": "Pocket-sized USB 3.2 Gen 2 solid-state drive with up to 1050MB/s read speed.",
                "price": Decimal("7499.00"),
                "stock": 2,
            },
            {
                "category": "Desk & Workspace",
                "name": "Ergonomic Mesh Office Chair",
                "description": "Breathable high-back chair with adjustable lumbar support and armrests.",
                "price": Decimal("8999.00"),
                "stock": 3,
            },
            {
                "category": "Desk & Workspace",
                "name": "Magnetic Cable Organizer Set",
                "description": "Silicone weighted desk cable clips to keep charging cords tidy.",
                "price": Decimal("449.00"),
                "stock": 18,
            },
            {
                "category": "Books & Stationery",
                "name": "Designing Data-Intensive Applications",
                "description": "Comprehensive guide to scalable, reliable, and maintainable software systems.",
                "price": Decimal("1450.00"),
                "stock": 6,
            },
            {
                "category": "Books & Stationery",
                "name": "Metal Fountain Pen Set",
                "description": "Matte black brass fountain pen with medium nib and refillable converter.",
                "price": Decimal("899.00"),
                "stock": 10,
            },
            {
                "category": "Lifestyle & Drinkware",
                "name": "Ceramic Pour-Over Coffee Dripper",
                "description": "Ribbed stoneware coffee brewer for clean, aromatic single-cup brewing.",
                "price": Decimal("749.00"),
                "stock": 9,
            },
            {
                "category": "Lifestyle & Drinkware",
                "name": "Tech Travel Organizer Pouch",
                "description": "Compact zippered case with elastic loops for chargers, SSDs, and cables.",
                "price": Decimal("699.00"),
                "stock": 14,
            },
            {
                "category": "Home & Audio",
                "name": "Compact Bluetooth Desktop Speaker",
                "description": "Stereo wireless speaker with rich bass, AUX input, and 15-hour playtime.",
                "price": Decimal("3299.00"),
                "stock": 2,
            },
            {
                "category": "Home & Audio",
                "name": "Smart Wi-Fi LED Light Strip (5m)",
                "description": "RGBIC ambient desk backlight controllable via app and voice assistants.",
                "price": Decimal("1199.00"),
                "stock": 11,
            },
        ]

        for item in more_products:
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
            status = "Created" if created else "Already exists"
            self.stdout.write(f"{status}: {product.name} [{cat_obj.name}]")
