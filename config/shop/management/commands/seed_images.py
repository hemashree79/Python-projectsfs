import os
import urllib.request
from django.conf import settings
from django.core.management.base import BaseCommand
from shop.models import Product

# Curated real product photos mapped by keyword in product name
PHOTO_KEYWORDS = [
    ("led light strip", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80"),
    ("speaker", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80"),
    ("organizer pouch", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80"),
    ("coffee dripper", "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=800&q=80"),
    ("fountain pen", "https://images.unsplash.com/photo-1585336261022-680e295ce3fe?auto=format&fit=crop&w=800&q=80"),
    ("data-intensive", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80"),
    ("clean code", "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=800&q=80"),
    ("notebook", "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=800&q=80"),
    ("cable organizer", "https://images.unsplash.com/photo-1586210579191-33b45e38fa2c?auto=format&fit=crop&w=800&q=80"),
    ("chair", "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?auto=format&fit=crop&w=800&q=80"),
    ("ssd", "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=800&q=80"),
    ("webcam", "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=800&q=80"),
    ("backpack", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80"),
    ("tumbler", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=80"),
    ("riser", "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80"),
    ("desk mat", "https://images.unsplash.com/photo-1616628188859-7a11abb6fcc9?auto=format&fit=crop&w=800&q=80"),
    ("desk lamp", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=800&q=80"),
    ("mouse", "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80"),
    ("monitor", "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80"),
    ("headphones", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80"),
    ("keyboard", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80"),
]

DEFAULT_PHOTO = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80"


class Command(BaseCommand):
    help = "Downloads real product photography for every product in the catalog."

    def handle(self, *args, **options):
        media_dir = os.path.join(settings.MEDIA_ROOT, "products")
        os.makedirs(media_dir, exist_ok=True)

        opener = urllib.request.build_opener()
        opener.addheaders = [("User-Agent", "Mozilla/5.0")]
        urllib.request.install_opener(opener)

        updated = 0
        for prod in Product.objects.all():
            lower_name = prod.name.lower()
            url = DEFAULT_PHOTO
            for keyword, photo_url in PHOTO_KEYWORDS:
                if keyword in lower_name:
                    url = photo_url
                    break

            filename = f"product_{prod.id}.jpg"
            filepath = os.path.join(media_dir, filename)
            try:
                urllib.request.urlretrieve(url, filepath)
                prod.image.name = f"products/{filename}"
                prod.save(update_fields=["image"])
                updated += 1
                self.stdout.write(f"Downloaded photo for: {prod.name}")
            except Exception as e:
                self.stdout.write(f"Skipped {prod.name}: {e}")

        self.stdout.write(f"Done! Updated {updated} products with real photos.")
