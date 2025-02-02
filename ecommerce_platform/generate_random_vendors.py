import os
import django
import random
import string
from faker import Faker
from django.utils.crypto import get_random_string
import requests
from django.core.files.base import ContentFile

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from vendors.models import VendorDetails

User = get_user_model()
fake = Faker()

def fetch_random_image():
    """Fetch a random image from an online placeholder service or use a local placeholder."""
    try:
        response = requests.get("https://picsum.photos/200", stream=True)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"shop_logo_{get_random_string(8)}.jpg")
    except requests.exceptions.RequestException:
        print("Failed to fetch image from the internet. Using local placeholder.")
    # Local placeholder fallback
    local_image_path = "path_to_local_placeholder/shop_logo.jpg"
    if os.path.exists(local_image_path):
        with open(local_image_path, "rb") as img_file:
            return ContentFile(img_file.read(), name="shop_logo_placeholder.jpg")
    return None

def create_random_vendors(count=20):
    for _ in range(count):
        # Generate realistic random user details
        email = fake.email()
        password = "SecurePassword123"
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone_number = fake.phone_number().replace(" ", "")[:10]  # Ensure 10 digits

        # Create User object
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user_type="vendor",
        )

        # Generate random vendor details
        shop_name = fake.company()
        shop_address = fake.address()
        bank_account_number = ''.join(random.choices(string.digits, k=12))
        bank_name = fake.company()
        ifsc_code = f"IFSC{get_random_string(6).upper()}"
        state = fake.state()
        city = fake.city()
        pincode = fake.postcode()

        # Fetch a random shop logo
        shop_logo = fetch_random_image()

        # Create VendorDetails object
        VendorDetails.objects.create(
            user=user,
            shop_name=shop_name,
            address=shop_address,
            bank_account_number=bank_account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code,
            state=state,
            city=city,
            pincode=pincode,
            is_verified=False,
            shop_logo=shop_logo,  # Assign the fetched shop logo
        )

    print(f"Successfully created {count} random vendors.")

# Call the function
if __name__ == "__main__":
    create_random_vendors()
