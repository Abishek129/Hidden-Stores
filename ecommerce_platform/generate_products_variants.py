import os
import django
import random
from faker import Faker
from django.utils.crypto import get_random_string
import requests
from django.core.files.base import ContentFile

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')
django.setup()

from products.models import Product, ProductVariant, ProductImage, VariantImage, AttributeValue
from vendors.models import VendorDetails
from products.models import Category

fake = Faker()

# Predefined categories for HD image retrieval
IMAGE_CATEGORIES = [
    "technology", "fashion", "home", "food", "sports", "books", "beauty", "toys", "automotive", "health"
]

IMAGE_FALLBACK_URL = "https://picsum.photos/1920/1080"


def fetch_hd_image(category):
    """Fetch high-quality HD image from Picsum or use a fallback."""
    image_url = f"https://picsum.photos/1920/1080?random={random.randint(1, 10000)}"
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"{category}_{get_random_string(5)}.jpg")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch image for category: {category}. Error: {e}")
    # Use fallback image
    try:
        fallback_response = requests.get(IMAGE_FALLBACK_URL, stream=True)
        if fallback_response.status_code == 200:
            return ContentFile(fallback_response.content, name=f"fallback_{get_random_string(5)}.jpg")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch fallback image. Error: {e}")
    return None


def create_products():
    vendors = VendorDetails.objects.all()
    products_per_vendor = 10
    variants_per_product = 4
    images_per_product = 3
    images_per_variant = 5

    for vendor in vendors:
        for _ in range(products_per_vendor):
            # Select a random category
            category = random.choice(Category.objects.all())
            category_name = category.name.lower()

            # Ensure `is_returnable` and `max_return_days` are consistent
            is_returnable = random.choice([True, False])
            max_return_days = random.randint(5, 30) if is_returnable else None

            # Create the product
            product_name = f"{fake.word().capitalize()} {category_name.capitalize()}"
            product = Product.objects.create(
                vendor=vendor,
                name=product_name,
                slug=f"{product_name.lower().replace(' ', '-')}-{get_random_string(4)}",
                description=fake.text(max_nb_chars=200),
                category=category,
                thumbnail=fetch_hd_image(category_name),
                stock=random.randint(50, 200),
                is_active=True,
                is_returnable=is_returnable,
                max_return_days=max_return_days,
                is_cancelable=random.choice([True, False]),
                cancellation_stage=random.choice(["before_packing", "before_shipping", "before_delivery"]),
                is_cod_allowed=random.choice([True, False]),
            )

            # Add product images
            for _ in range(images_per_product):
                image = fetch_hd_image(category_name)
                if image:
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                    )

            # Create variants
            for _ in range(variants_per_product):
                variant = ProductVariant.objects.create(
                    product=product,
                    base_price=round(random.uniform(100.00, 1000.00), 2),
                    offer_price=round(random.uniform(50.00, 900.00), 2),
                    stock=random.randint(10, 100),
                )

                # Assign random attributes to the variant
                attributes = AttributeValue.objects.order_by('?')[:2]  # Randomly select 2 attributes
                variant.attributes.set(attributes)

                # Add variant images
                for _ in range(images_per_variant):
                    image = fetch_hd_image(category_name)
                    if image:
                        VariantImage.objects.create(
                            product_variant=variant,
                            image=image,
                        )

        print(f"Created {products_per_vendor} products for vendor: {vendor.user.email}")

    print("Product creation completed successfully.")

# Run the script
if __name__ == "__main__":
    create_products()
