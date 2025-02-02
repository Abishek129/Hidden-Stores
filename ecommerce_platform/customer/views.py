from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from cart_orders.models import OrderItem
from vendors.serializers import OrderItemSerializer
from .models import *
from .serializers import *
from products.models import *
from vendors.models import *
from products.serializers import *


class AllProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all products with pagination."""
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Fetch product details by product ID."""
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all categories."""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AllAttributesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all attributes."""
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AttributeDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Fetch details of a specific attribute."""
        attribute = get_object_or_404(Attribute, pk=pk)
        serializer = AttributeSerializer(attribute)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllAttributeValuesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all attribute values."""
        attribute_values = AttributeValue.objects.all()
        serializer = AttributeValueSerializer(attribute_values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AttributeValueDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Fetch details of a specific attribute value."""
        attribute_value = get_object_or_404(AttributeValue, pk=pk)
        serializer = AttributeValueSerializer(attribute_value)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


from products.models import ProductVariant
from products.serializers import ProductVariantSerializer

class ProductVariantsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        """Fetch all variants for a specific product."""
        product = get_object_or_404(Product, id=product_id)
        variants = ProductVariant.objects.filter(product=product)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProductSearchView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        search_query = request.query_params.get('search', '').strip()
        if not search_query:
            return Response({"detail": "Search query is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initial search by slug
        search_terms = search_query.split()
        query = Q()
        for term in search_terms:
            query |= Q(slug__icontains=term)
        products = Product.objects.filter(query).distinct()

        # Filter by price range
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price or max_price:
            variants_query = Q()
            if min_price:
                variants_query &= Q(variants__offer_price__gte=float(min_price))
            if max_price:
                variants_query &= Q(variants__offer_price__lte=float(max_price))
            products = products.filter(variants_query)

        # Filter by attribute values
        attribute_values = request.query_params.getlist('attribute_values')  # Example: ['1', '2', '3']
        if attribute_values:
            products = products.filter(variants__attributes__id__in=attribute_values).distinct()

        # Serialize and return filtered results
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



# Customer paid orders

class PaidOrderItemsView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this endpoint

    def get(self, request):
        # Get the currently authenticated user
        user = request.user

        # Filter OrderItems with payment_status "paid" and Orders linked to the user
        paid_items = OrderItem.objects.filter(
            payment_status="paid",
            order__customer=user
        )

        # Serialize the data
        serializer = OrderItemSerializer(paid_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




# Product review

class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ensure the user is a customer
        if request.user.user_type != 'customer':
            return Response(
                {"detail": "Only customers can create reviews."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Set the customer field to the authenticated user
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get("product")
        if not product_id:
            return Response(
                {"detail": "Product ID is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        review_id = kwargs.get("review_id")
        try:
            review = Review.objects.get(id=review_id, customer=request.user)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found or you are not authorized to delete it."},
                status=status.HTTP_404_NOT_FOUND
            )

        review.delete()
        return Response({"detail": "Review deleted successfully."}, status=status.HTTP_200_OK)


class RefundInitiateView(APIView):
    """
    Endpoint to initiate a refund for a given order item.


    """

    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RefundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Refund initiated successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RefundDetailView(APIView):
    def get(self, request, refund_id):
        try:
            refund = Refund.objects.get(id=refund_id)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RefundDetailSerializer(refund)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ProductsByShopNameView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, shop_name):
        try:
            # Get vendor with the given shop name
            vendor = VendorDetails.objects.get(shop_name=shop_name)
            # Filter products for this vendor
            products = Product.objects.filter(vendor=vendor)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VendorDetails.DoesNotExist:
            return Response({"error": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# customers/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import FeaturedProduct
from .serializers import FeaturedProductDetailSerializer

class FeaturedProductListView(APIView):
    permission_classes = []  # Open to all users (no authentication required)

    def get(self, request):
        # Fetch all featured products
        featured_products = FeaturedProduct.objects.select_related('product', 'vendor').all()
        serializer = FeaturedProductDetailSerializer(featured_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from banners.models import Banner, ScrollableBanner
from banners.serializers import BannerSerializer, ScrollableBannerSerializer


class BannersView(APIView):
    """
    View to fetch all banners (bottom and scrollable).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Fetch active banners
        bottom_banners = Banner.objects.filter(is_active=True).order_by('-priority', 'created_at')
        scrollable_banners = ScrollableBanner.objects.filter(is_active=True).order_by('-priority', 'created_at')

        # Serialize data
        bottom_banners_serializer = BannerSerializer(bottom_banners, many=True)
        scrollable_banners_serializer = ScrollableBannerSerializer(scrollable_banners, many=True)

        return Response({
            "bottom_banners": bottom_banners_serializer.data,
            "scrollable_banners": scrollable_banners_serializer.data
        })
