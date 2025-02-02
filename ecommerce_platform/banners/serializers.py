from rest_framework import serializers
from .models import Banner, ScrollableBanner

class BannerSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id',
            'title',
            'image',
            'banner_type',
            'category',
            'category_name',
            'vendor',
            'vendor_name',
            'external_url',
            'priority',
            'is_active',
            'created_at',
        ]


class ScrollableBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrollableBanner
        fields = [
            'id',
            'title',
            'image',
            'external_url',
            'priority',
            'is_active',
            'created_at',
        ]
