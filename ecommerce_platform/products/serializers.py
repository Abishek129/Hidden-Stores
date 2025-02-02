from rest_framework import serializers
from .models import Category, Attribute, AttributeValue, Product, ProductVariant, ProductImage
from rest_framework.exceptions import ValidationError

# ================================
# Category Serializer
# ================================
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    icon = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'subcategories', 'icon']

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data

# ================================
# Attribute and Attribute Value Serializers
# ================================
class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'value', 'slug']

class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'slug', 'values']

# ================================
# Product Image Serializer
# ================================
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']

# ================================
# Product Variant Serializer
# ================================

from .models import VariantImage

class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ['id', 'product_variant', 'image']


class ProductVariantSerializer(serializers.ModelSerializer):
    # Allow writable attribute linking
    attributes = serializers.PrimaryKeyRelatedField(queryset=AttributeValue.objects.all(), many=True)
    discount_percentage = serializers.ReadOnlyField()
    images = VariantImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'attributes', 'base_price', 'offer_price',
            'discount_percentage', 'stock', 'sku', 'images'
        ]

    def create(self, validated_data):
        attributes = validated_data.pop('attributes', [])
        product = validated_data.get('product')

        # Check if a variant with the same attributes already exists
        existing_variants = ProductVariant.objects.filter(product=product)
        for variant in existing_variants:
            existing_attribute_ids = set(variant.attributes.values_list('id', flat=True))
            new_attribute_ids = set([attr.id for attr in attributes])
            if existing_attribute_ids == new_attribute_ids:
                raise ValidationError("A product variant with the same attribute values already exists.")

        # Create the product variant if it doesn't exist
        product_variant = ProductVariant.objects.create(**validated_data)
        product_variant.attributes.set(attributes)
        product.stock += product_variant.stock
        if product.is_cancelable and not product.cancellation_stage:
            
            product.cancellation_stage = "Default Stage"
        product.save()  # Link ManyToMany field after creation
        return product_variant

    def update(self, instance, validated_data):
        attributes = validated_data.pop('attributes', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if attributes:
            instance.attributes.set(attributes)  # Update ManyToMany field
        return instance



# ================================
# Product Serializer
# ================================
from rest_framework import serializers
from .models import Product
from .serializers import ProductVariantSerializer, ProductImageSerializer

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'thumbnail', 'is_returnable', 'max_return_days', 'is_cancelable', 'cancellation_stage', 'is_cod_allowed',
            'created_at', 'updated_at', 'variants', 'images', 'stock',
        ]

    def validate(self, data):
        # Validate is_returnable and max_return_days
        if data.get('is_returnable') and not data.get('max_return_days'):
            raise serializers.ValidationError({"max_return_days": "This field is required if the product is returnable."})

        # Validate is_cancelable and cancellation_stage
        if data.get('is_cancelable') and not data.get('cancellation_stage'):
            raise serializers.ValidationError({"cancellation_stage": "This field is required if the product is cancelable."})
        
        return data




# App: products/serializers.py

from rest_framework import serializers
from .models import FeaturedProduct

class FeaturedProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='vendor.shop_name', read_only=True)

    class Meta:
        model = FeaturedProduct
        fields = ['id', 'product', 'added_at','store_name']
        read_only_fields = ['vendor']  # Prevent vendor from being passed in the request


from rest_framework import serializers
from .models import Product

class ProductFilterSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    store_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    price = serializers.SerializerMethodField()  # Fetch the offer price dynamically
    base_price = serializers.SerializerMethodField()  # Fetch the base price dynamically

    class Meta:
        model = Product
        fields = ['id', 'store_name', 'name', 'category', 'category_name', 'thumbnail', 'price', 'base_price', 'stock']

    def get_price(self, obj):
        # Fetch the offer price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().offer_price  # Use offer_price from the variant
        return None  # Return None if no variants

    def get_base_price(self, obj):
        # Fetch the base price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().base_price  # Use base_price from the variant
        return None  # Return None if no variants


from rest_framework import serializers
from .models import Product

class NewArrivalsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    store_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    base_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()  # Fetch price dynamically from the first variant

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'store_name',
            'category',
            'category_name',
            'thumbnail',
            'created_at',
            'stock',
            'price',
            'base_price',
        ]

    def get_price(self, obj):
        # Fetch the price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().offer_price  # Use offer_price field from the variant
        return None  # Return None if no variants are available

    def get_base_price(self, obj):
        # Fetch the base price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().base_price  # Use base_price field from the variant
        return None  # Return None if no variants are available