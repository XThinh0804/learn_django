import django_filters
from api.models import Product, Order
from rest_framework import filters


class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0) # Chỉ lấy những sản phẩm có stock lớn hơn 0

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name' : ['iexact', 'icontains'],
            'price' : ['exact', 'lt', 'gt', 'range'],
        }

class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date')#Chỉ lọc theo ngày
    class Meta:
        model = Order
        fields = {
            'status' : ['iexact'],
            'created_at' : ['exact', 'lt', 'gt'],
        }