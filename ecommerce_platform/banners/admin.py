from django.contrib import admin
from .models import Banner, ScrollableBanner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'category', 'vendor', 'priority', 'is_active', 'created_at', 'updated_at')
    list_filter = ('banner_type', 'is_active', 'created_at')
    search_fields = ('title', 'category__name', 'vendor__shop_name')
    ordering = ['-priority', 'created_at']
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'banner_type', 'category', 'vendor', 'external_url', 'priority', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ScrollableBanner)
class ScrollableBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    ordering = ['-priority', 'created_at']
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'external_url', 'priority', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
