from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from customer.views import RefundDetailView

router = DefaultRouter()
router.register(r'warehouse-address', WareHouseAddressViewSet, basename='warehouse-address')


urlpatterns = [
    # Admin Logs
    path('logs/', AdminLogView.as_view(), name='admin-logs'),
    
    #Vendor Approvals
    path('vendor-approved/<int:id>/', VendorProfileUpdateView.as_view(), name='vendor-profile-update'),
    path('vendor-profile/<int:id>/', VendorProfileDetailView.as_view(), name='vendor-profile-detail'),

    # Vendor Payouts
    path('payouts/', VendorPayoutView.as_view(), name='vendor-payouts'),
    path('payouts/<int:payout_id>/', VendorPayoutView.as_view(), name='vendor-payout-detail'),

    # Refunds
    path('refunds/<int:refund_id>/', RefundDetailView.as_view(), name='refund-detail'),
    path('refunds/<int:refund_id>/<str:action>/', RefundActionView.as_view(), name='refund-action'),


    # orders places
    path('orders/placed/', ListPlacedOrdersView.as_view(), name='list-placed-orders'),

    path('soft-data/', CreateSoftDataView.as_view(), name='create-soft-data'),

    # Xpress bees login
    path('xpressbee/login/', XpressBeeLogin.as_view(), name = 'xpress-bee-login'),
    path('create/shipments/', CreateXpressBeeShipment.as_view(), name = 'shipment'),
    path('return/shipment', CreateReturnShipment.as_view(), name = 'return-shipment'),
    path('track-shipment/', TrackXpressBeeShipment.as_view(), name = 'track-shipment'),
    path('generate-manifest/', GenerateManifestXpressBee.as_view(), name = 'generate-manifest' ),
    path('cancel-shipment/', CancelShipmentXpressBee.as_view(), name = 'cancel-shipment'),
    path('webhook/', XpressBeesWebhook.as_view(), name = 'xpressbees_webhook'),
    path('', include(router.urls)),
    
]
