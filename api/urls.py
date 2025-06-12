from django.urls import path
from . import views

urlpatterns = [
    path('products/',views.product_list,name='get_all_products'),
    path('products/info',views.product_info,name='get_product_info'),
    path('products/<int:pk>/',views.product_detail, name='get_product_by_id'),
    path('orders/',views.order_list,name='get_all_orders'),
]