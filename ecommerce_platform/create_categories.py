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

from products.models import Category

fake = Faker()

def fetch_unique_image():
    """Fetch a completely unique image for each category."""
    try:
        # Generate a truly unique image URL by appending a random string to the seed
        unique_seed = get_random_string(10)
        image_url = f"https://picsum.photos/seed/{unique_seed}/200"
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"category_{unique_seed}.jpg")
    except requests.exceptions.RequestException:
        print("Failed to fetch a unique image.")
    return None

def create_categories():
    """Create a hierarchy of categories with unique slugs and images."""
    root_categories = [
        "Electronics", "Fashion", "Home", "Food", "Sports",
        "Books", "Beauty", "Toys", "Automotive", "Health"
    ]

    for root in root_categories:
        # Create root category
        root_category, created = Category.objects.get_or_create(
            name=root,
            defaults={
                "slug": f"{root.lower().replace(' ', '-')}-{get_random_string(4)}",
                "icon": fetch_unique_image(),
            }
        )

        if created:
            print(f"Created root category: {root}")

        # Create subcategories
        for _ in range(5):
            subcategory_name = f"{root} {fake.word().capitalize()}"
            subcategory, created = Category.objects.get_or_create(
                name=subcategory_name,
                parent=root_category,
                defaults={
                    "slug": f"{subcategory_name.lower().replace(' ', '-')}-{get_random_string(4)}",
                    "icon": fetch_unique_image(),
                }
            )

            if created:
                print(f"Created subcategory: {subcategory_name} under {root}")

            # Create sub-subcategories
            for _ in range(2):
                sub_subcategory_name = f"{subcategory_name} {fake.word().capitalize()}"
                sub_subcategory, created = Category.objects.get_or_create(
                    name=sub_subcategory_name,
                    parent=subcategory,
                    defaults={
                        "slug": f"{sub_subcategory_name.lower().replace(' ', '-')}-{get_random_string(4)}",
                        "icon": fetch_unique_image(),
                    }
                )

                if created:
                    print(f"Created sub-subcategory: {sub_subcategory_name} under {subcategory_name}")

    print("Category hierarchy creation complete.")

# Run the script
if __name__ == "__main__":
    create_categories()
