from django.contrib import admin
from .models import VendorDetails

@admin.register(VendorDetails)
class VendorDetailsAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'is_verified', 'created_at', 'updated_at')
    search_fields = ('user__email', 'bank_name', 'ifsc_code')
    list_filter = ('is_verified',)

    @admin.action(description='Mark selected vendors as verified')
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
