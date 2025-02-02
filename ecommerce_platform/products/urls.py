from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    AttributeListCreateView, 
    AttributeDetailView,
    AttributeValueListCreateView, 
    AttributeValueDetailView,
    ProductListCreateView, 
    ProductDetailView,
    ProductVariantListCreateView, 
    ProductVariantDetailView,
    ProductImageListCreateView, 
    ProductImageDetailView,
    LeafCategoriesByParentView,
    VariantImageDetailView,
    FeaturedProductListCreateView,
    ProductFilterByCategoryView,
    NewArrivalsView,
    ProductListView,

)

urlpatterns = [
    # Category URLs
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:parent_id>/leaf/', LeafCategoriesByParentView.as_view(), name='leaf-categories'),

    # Attribute URLs
    path('attributes/', AttributeListCreateView.as_view(), name='attribute-list-create'),
    path('attributes/<int:pk>/', AttributeDetailView.as_view(), name='attribute-detail'),
    path('attribute-values/', AttributeValueListCreateView.as_view(), name='attribute-value-list-create'),
    path('attribute-values/<int:pk>/', AttributeValueDetailView.as_view(), name='attribute-value-detail'),

    # Product URLs
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Product Variant URLs
    path('variants/', ProductVariantListCreateView.as_view(), name='variant-list-create'),
    path('variants/<int:pk>/', ProductVariantDetailView.as_view(), name='variant-detail'),
    path('variants/images/<int:pk>/', VariantImageDetailView.as_view(), name='variant-image-detail'),

    # Product Image URLs
    path('images/', ProductImageListCreateView.as_view(), name='image-list-create'),
    path('images/<int:pk>/', ProductImageDetailView.as_view(), name='image-detail'),

    path('featured-products/', FeaturedProductListCreateView.as_view(), name='featured-products'),

    path('products/filter/', ProductFilterByCategoryView.as_view(), name='product-filter'),
    
    path('products/new-arrivals/', NewArrivalsView.as_view(), name='new-arrivals'),

    path('filter-category-products/', ProductListView.as_view(), name='filter-category-products'),

    
]
