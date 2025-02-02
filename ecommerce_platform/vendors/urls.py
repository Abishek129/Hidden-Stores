from django.urls import path
from .views import *
from django.urls import re_path
from customer.views import RefundDetailView

urlpatterns = [
    path('details/', VendorDetailsView.as_view(), name='vendor-details'),
    path('media/<path:path>', serve_media, name='serve_media'),
    path('vendor/paid-order-items/', VendorPaidOrderItemsView.as_view(), name='vendor-paid-order-items'),
    path('dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('order-items/<int:order_item_id>/update-status/', VendorOrderStatusUpdateView.as_view(), name='vendor-update-status'),
    path('order-status-options/', OrderStatusOptionsView.as_view(), name='order-status-options'),
    path('refunds/<int:refund_id>/', RefundDetailView.as_view(), name='refund-detail'),
    path('shops/', VendorShopListView.as_view(), name='vendor-shops'),

    
]

urlpatterns += [
    re_path(r'^media/(?P<path>.+)$', serve_media, name='serve_media'),
]