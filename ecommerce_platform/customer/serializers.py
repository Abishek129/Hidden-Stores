from rest_framework import serializers
from .models import *
from cart_orders.models import *
from products.models import *

class ReviewMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewMedia
        fields = ['media']

class ReviewSerializer(serializers.ModelSerializer):
    media = ReviewMediaSerializer(many=True, required=False, write_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Review
        fields = ['product', 'review_text', 'rating', 'media']

    def validate_rating(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value

    def create(self, validated_data):
        media_data = validated_data.pop('media', [])
        review = Review.objects.create(**validated_data)
        for media_item in media_data:
            ReviewMedia.objects.create(review=review, media=media_item['media'])
        return review



from rest_framework import serializers
from admin_portal.models import Refund, RefundMedia
from cart_orders.models import OrderItem
from django.utils import timezone


class RefundMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundMedia
        fields = ['media']

class RefundSerializer(serializers.ModelSerializer):
    media = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        help_text="List of media files (images/videos) for the refund"
    )
    order_id = serializers.IntegerField(write_only=True, help_text="ID of the order item to refund")
    reason = serializers.CharField(max_length=500, required=True, help_text="Reason for the refund")

    class Meta:
        model = Refund
        fields = ['order_id', 'reason', 'media']

    def create(self, validated_data):
        order_id = validated_data.pop('order_id')
        media_files = validated_data.pop('media', [])
        reason = validated_data['reason']

        # Ensure the order item exists
        try:
            order_item = OrderItem.objects.get(pk=order_id)
        except OrderItem.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Invalid order ID."})

        # Create refund
        refund = Refund.objects.create(
            order_item=order_item,
            reason=reason,
            amount=order_item.price,  # Assuming `price` field exists in OrderItem
            status='initiated',
            refund_initiated_date=timezone.now()
        )

        # Save media files
        for file in media_files:
            RefundMedia.objects.create(refund=refund, media=file)

        return refund


class RefundMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundMedia
        fields = ['id', 'media']

class RefundDetailSerializer(serializers.ModelSerializer):
    media = RefundMediaSerializer(source='refundmedia_set', many=True)  # Access related media

    class Meta:
        model = Refund
        fields = [
            'id', 'order_item', 'amount', 'reason', 'refund_status',
            'refund_initiated_date', 'refund_processed_date',
            'refund_rejected_date', 'refund_implemented_date', 'media',
        ]
        depth = 1



# customers/serializers.py

from rest_framework import serializers
from products.models import FeaturedProduct

class FeaturedProductDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    product_thumbnail = serializers.ImageField(source='product.thumbnail', read_only=True)  # Fetch the thumbnail directly
    price = serializers.SerializerMethodField()  # Fetch the offer price dynamically
    base_price = serializers.SerializerMethodField()  # Fetch the base price dynamically

    class Meta:
        model = FeaturedProduct
        fields = ['id', 'product', 'product_name', 'vendor', 'vendor_name', 'product_thumbnail', 'price', 'base_price', 'added_at']

    def get_price(self, obj):
        # Get the offer price of the first available variant
        if obj.product.variants.exists():
            first_variant = obj.product.variants.first()
            return first_variant.offer_price  # Use offer_price from the variant
        return None  # Return None if no variants exist

    def get_base_price(self, obj):
        # Get the base price of the first available variant
        if obj.product.variants.exists():
            first_variant = obj.product.variants.first()
            return first_variant.base_price  # Use base_price from the variant
        return None  # Return None if no variants exist
