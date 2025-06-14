from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('products/',views.ProductListCreateAPIView.as_view(),name='get_all_products'),
    path('products/info',views.ProductInfoAPIView.as_view(),name='get_product_info'),
    path('products/<int:pk>/',views.ProductDetailAPIView.as_view(), name='get_product_by_id'),
]

router = DefaultRouter()
router.register('orders', views.OrderViewSet)
urlpatterns += router.urls