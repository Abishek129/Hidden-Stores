from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Category, Attribute, AttributeValue, Product, ProductVariant, ProductImage
from .serializers import (
    CategorySerializer,
    AttributeSerializer,
    AttributeValueSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ProductImageSerializer
)

# ================================
# Category Views
# ================================
class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

# ================================
# Leaf Category Views
# ================================

class LeafCategoriesByParentView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, parent_id):
        try:
            parent_category = Category.objects.get(id=parent_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)

        # Fetch all leaf categories under the selected category
        leaf_categories = parent_category.get_leaf_categories()
        serializer = CategorySerializer(leaf_categories, many=True)
        return Response(serializer.data)

# ================================
# Attribute Views
# ================================
class AttributeListCreateView(ListCreateAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class AttributeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class AttributeValueListCreateView(ListCreateAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class AttributeValueDetailView(RetrieveUpdateDestroyAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

# ================================
# Product Views
# ================================
class ProductListCreateView(ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Filter products by the vendor of the logged-in user
        return Product.objects.filter(vendor=self.request.user.vendor_details)

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Save the product with the vendor set to the logged-in user's vendor details
        serializer.save(vendor=self.request.user.vendor_details)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

# ================================
# Product Variant Views
# ================================
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import ProductVariant, VariantImage
from .serializers import ProductVariantSerializer
from rest_framework import serializers

class ProductVariantListCreateView(ListCreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        product_variant = serializer.save()
        images = self.request.FILES.getlist('images')
        for image in images:
            VariantImage.objects.create(product_variant=product_variant, image=image)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)


class ProductVariantDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        # Update the product variant
        product_variant = serializer.save()

        # Handle nested image updates
        images = self.request.FILES.getlist('images')  # Expect multiple files with key 'images'
        if images:
            # Clear existing images
            VariantImage.objects.filter(product_variant=product_variant).delete()
            # Add new images
            for image in images:
                VariantImage.objects.create(product_variant=product_variant, image=image)



# ================================
# Product Image Views
# ================================
class ProductImageListCreateView(ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class ProductImageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


from rest_framework.generics import RetrieveDestroyAPIView
from .models import VariantImage
from .serializers import VariantImageSerializer

class VariantImageDetailView(RetrieveDestroyAPIView):
    """
    Allows retrieving and deleting a specific VariantImage by its primary key.
    """
    queryset = VariantImage.objects.all()
    serializer_class = VariantImageSerializer




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FeaturedProduct, Product
from .serializers import FeaturedProductSerializer
from vendors.models import VendorDetails
from django.core.exceptions import ValidationError

class FeaturedProductListCreateView(APIView):
    def get(self, request):
        # Fetch the vendor for the logged-in user
        try:
            vendor = VendorDetails.objects.get(user=request.user)
        except VendorDetails.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all featured products for the logged-in vendor
        featured_products = FeaturedProduct.objects.filter(vendor=vendor)
        serializer = FeaturedProductSerializer(featured_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Fetch the vendor for the logged-in user
        try:
            vendor = VendorDetails.objects.get(user=request.user)
        except VendorDetails.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate the product belongs to the logged-in vendor
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id, vendor=vendor)
        except Product.DoesNotExist:
            return Response({"detail": "This product does not belong to you."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save the featured product
        if vendor.featured_products.count() >= 10:
            return Response({"detail": "You can only have up to 10 featured products."}, status=status.HTTP_400_BAD_REQUEST)

        featured_product = FeaturedProduct(vendor=vendor, product=product)
        try:
            featured_product.save()
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeaturedProductSerializer(featured_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Product, Category
from .serializers import ProductFilterSerializer


class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for product filtering.
    """
    page_size = 6  # Number of products per page
    page_size_query_param = 'page_size'  # Allow users to set page size via query
    max_page_size = 100  # Maximum products per page


class ProductFilterByCategoryView(ListAPIView):
    """
    API view to filter products by category, including subcategories.
    """
    serializer_class = ProductFilterSerializer
    pagination_class = ProductPagination
    permission_classes = []  # Open to all users (no authentication required)

    def get_queryset(self):
        # Get the category ID from the query parameters
        category_id = self.request.query_params.get('category_id')
        if not category_id:
            return Product.objects.none()  # Return an empty queryset if no category ID

        try:
            # Get the selected category
            category = Category.objects.get(id=category_id)

            # Fetch all subcategories, including the selected category
            subcategories = Category.objects.filter(Q(id=category.id) | Q(parent=category))

            # Return filtered products for the subcategories
            return Product.objects.filter(category__in=subcategories, is_active=True).select_related('category')

        except Category.DoesNotExist:
            return Product.objects.none()  # Return an empty queryset if the category is not found




from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .models import Product
from .serializers import NewArrivalsSerializer
from datetime import timedelta
from django.utils.timezone import now

class NewArrivalsPagination(PageNumberPagination):
    page_size = 8  # Default number of products per page
    page_size_query_param = 'page_size'  # Allow frontend to set the page size
    max_page_size = 90 # Limit the maximum number of products per page

class NewArrivalsView(ListAPIView):
    serializer_class = NewArrivalsSerializer
    pagination_class = NewArrivalsPagination


    permission_classes = []
    def get_queryset(self):
        # Define the time window for "New Arrivals" (e.g., last 30 days)
        new_arrivals_window = now() - timedelta(days=30)

        # Get products within the new arrivals window
        new_products = Product.objects.filter(created_at__gte=new_arrivals_window).order_by('-created_at')

        # If fewer than the desired count, add older products to fill the gap
        if new_products.count() < self.pagination_class.page_size:
            fallback_products = Product.objects.exclude(id__in=new_products).order_by('-created_at')[:self.pagination_class.page_size - new_products.count()]
            return new_products | fallback_products  # Combine querysets

        return new_products



from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from products.models import Product, Category
from products.serializers import ProductSerializer

class ProductPagination(PageNumberPagination):
    page_size = 8  # Limit to 8 products per page
    page_size_query_param = 'page_size'  # Allow clients to override page size
    max_page_size = 100  # Set a maximum limit for page size

class ProductListView(ListAPIView):
    """
    View to retrieve paginated products, including those from nested subcategories of a root category.
    """
    permission_classes = [AllowAny]  # Allow access to all users
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        # Get the root category ID from the request (e.g., query parameter or URL)
        root_category_id = self.request.query_params.get('category_id')
        if not root_category_id:
            return Product.objects.none()  # Return an empty queryset if no category ID is provided

        # Fetch the root category
        root_category = get_object_or_404(Category, id=root_category_id)

        # Get all subcategories, including nested ones
        all_subcategories = root_category.get_all_subcategories()
        all_category_ids = [category.id for category in all_subcategories]
        all_category_ids.append(root_category.id)  # Include the root category itself

        # Query products for these categories
        return Product.objects.filter(category_id__in=all_category_ids, is_active=True)
