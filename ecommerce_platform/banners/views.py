from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from .models import Banner, ScrollableBanner
from .serializers import BannerSerializer, ScrollableBannerSerializer


# Pagination Class for Banners
class BannerPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow clients to control page size
    max_page_size = 50  # Maximum page size limit


class BannerListCreateView(ListCreateAPIView):
    """
    View to fetch all bottom banners (static banners linked to categories, vendors, or promotions).
    Includes pagination, filtering by banner type, and POST support for creating banners.
    """
    queryset = Banner.objects.all().order_by('-priority', 'created_at')
    serializer_class = BannerSerializer
    pagination_class = BannerPagination
    filter_backends = [SearchFilter]
    search_fields = ['banner_type']  # Allow filtering by banner type (CATEGORY, VENDOR, PROMOTIONAL)


class ScrollableBannerListCreateView(ListCreateAPIView):
    """
    View to fetch and create top scrollable banners.
    Includes pagination and POST support for creating banners.
    """
    queryset = ScrollableBanner.objects.all().order_by('-priority', 'created_at')
    serializer_class = ScrollableBannerSerializer
    pagination_class = BannerPagination  # Optional pagination for scrollable banners
