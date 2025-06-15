from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import InStockFilterBackend, OrderFilter, ProductFilter
from api.models import Order, Product, User
from api.serializers import (OrderSerializer,ProductInfoSerializer,
                            ProductSerializer, OrderCreateSerializer, UserSerializer)
from rest_framework.throttling import ScopedRateThrottle
from api.tasks import send_order_confirmation_email


# Create your views here.
@extend_schema(tags=["Products"])
class ProductListCreateAPIView(generics.ListCreateAPIView):
    throttle_scope = 'products'
    throttle_classes = [ScopedRateThrottle]
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]
    #SearchFilter:full text search
    search_fields = ['name', 'description']
    #OrderingFilter:cho phép sắp xếp theo trường nào đó
    ordering_fields = ['name','price','stock']
    # pagination_class = LimitOffsetPagination # Phân trang theo giới hạn và offset
    pagination_class = None
    # pagination_class = PageNumberPagination # Phân trang theo số trang
    # pagination_class.page_size = 2
    # pagination_class.page_query_param = 'pageNo' # Thay đổi tên tham số phân trang
    # pagination_class.page_size_query_param = 'pageSize' # Thay đổi tên tham số kích thước trang
    # pagination_class.max_page_size = 6

    @method_decorator(cache_page(60 * 5, key_prefix= 'product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    def get_queryset(self):
        import time
        time.sleep(2)  # Giả lập thời gian xử lý lâu
        return super().get_queryset()

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

@extend_schema(tags=["Products"])
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['DELETE', 'PUT', 'PATCH']:
            # Nếu là phương thức DELETE, PUT hoặc PATCH thì chỉ cho phép admin
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    # lookup_url_kwarg = 'product_id' nếu muốn sử dụng một tên khác thay pk trong URL

@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    throttle_scope = 'orders'
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @method_decorator(cache_page(60 * 15, key_prefix= 'order_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.save(user = self.request.user)
        send_order_confirmation_email.delay(order.order_id, self.request.user.email)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs =  super().get_queryset()
        if not self.request.user.is_staff:
            return qs.filter(user=self.request.user)
        return qs
    # @action(
    #         detail= False,
    #         methods=['get'],
    #         url_path='user-orders'
    # )
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many = True)
    #     return Response(serializer.data)

@extend_schema(tags=["Products"])
class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'] or 0
        })
        return Response(serializer.data)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None