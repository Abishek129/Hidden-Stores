from django.contrib import admin
from .models import Category, Attribute, AttributeValue, Product, ProductVariant, ProductImage, FeaturedProduct

# ================================
# Inline Admin for Related Models
# ================================

class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1  # Number of empty forms for adding new records

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1  # Number of empty forms for adding new variants

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms for adding new images

# ================================
# Admin Models
# ================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'slug')  # Columns to display in admin list view
    search_fields = ('name',)  # Searchable fields
    prepopulated_fields = {'slug': ('name',)}  # Auto-generate slug from name 
    list_filter = ('parent',)  # Filter categories by parent

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value', 'slug')
    search_fields = ('value', 'attribute__name')
    list_filter = ('attribute',)
    prepopulated_fields = {'slug': ('value',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vendor', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'vendor__user__email', 'category__name')
    list_filter = ('category', 'vendor')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'base_price', 'offer_price', 'stock', 'sku', 'discount_percentage')
    search_fields = ('product__name', 'sku')
    list_filter = ('product',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image')
    search_fields = ('product__name',)

# ================================
# Featured Product Admin
# ================================

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'product', 'added_at')  # Display vendor, product, and added timestamp
    search_fields = ('vendor__user__email', 'product__name')  # Enable searching by vendor email and product name
    list_filter = ('vendor', 'added_at')  # Enable filtering by vendor and added date
