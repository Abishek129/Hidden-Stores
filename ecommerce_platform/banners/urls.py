from django.urls import path
from .views import *

urlpatterns = [
    # URL for bottom banners (static banners linked to categories/vendors)
    path('bottom-banners/', BannerListCreateView.as_view(), name='bottom-banners'),
    
    # URL for top scrollable banners (carousel)
    path('scrollable-banners/', ScrollableBannerListCreateView.as_view(), name='scrollable-banners'),
]
