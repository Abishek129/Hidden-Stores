from django.db import models
from products.models import Category
from vendors.models import VendorDetails

class BannerType(models.TextChoices):
    PROMOTIONAL = 'PROMOTIONAL', 'Promotional'
    CATEGORY = 'CATEGORY', 'Category'
    VENDOR = 'VENDOR', 'Vendor'

class Banner(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Title of the banner")
    image = models.ImageField(upload_to="banners/", help_text="Image for the banner", null=True)  # Ensure image field is present
    banner_type = models.CharField(
        max_length=20, choices=BannerType.choices, help_text="Type of banner: Promotional, Category, or Vendor"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True, help_text="Linked category for the banner"
    )
    vendor = models.ForeignKey(
        VendorDetails, on_delete=models.CASCADE, blank=True, null=True, help_text="Linked vendor for the banner"
    )
    external_url = models.URLField(
        blank=True, null=True, help_text="External URL for promotional banners"
    )
    priority = models.PositiveIntegerField(default=0, help_text="Priority of the banner for ordering")
    is_active = models.BooleanField(default=True, help_text="Is the banner active?")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the banner was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the banner was last updated")

    class Meta:
        ordering = ['-priority', 'created_at']  # Higher priority banners appear first

    def __str__(self):
        return f"{self.title or 'Untitled Banner'} - {self.banner_type}"

class ScrollableBanner(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Title of the scrollable banner")
    image = models.ImageField(upload_to="scrollable_banners/", help_text="Image for the scrollable banner", null=True)  # Ensure image field is present
    external_url = models.URLField(
        blank=True, null=True, help_text="External URL for the scrollable banner"
    )
    priority = models.PositiveIntegerField(default=0, help_text="Priority of the scrollable banner for ordering")
    is_active = models.BooleanField(default=True, help_text="Is the scrollable banner active?")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the scrollable banner was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the scrollable banner was last updated")

    class Meta:
        ordering = ['-priority', 'created_at']  # Higher priority banners appear first

    def __str__(self):
        return self.title or "Untitled Scrollable Banner"
