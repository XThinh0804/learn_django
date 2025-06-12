from rest_framework import serializers
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
            'stock',
        )
    #validate price to be a positive decimal
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
class OrderItemSerializer(serializers.ModelSerializer):
    #product = ProductSerializer() #Hiển thị tất cả thông tin của product
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        read_only=True,
        max_digits=10,
        decimal_places=2)
    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal',
        )

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many = True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name= 'total')
    def total(self, obj):
        #return sum(item.item_subtotal for item in obj.items.all())
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)
    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'user',
            'status',
            'items',
            'total_price',
        )

class ProductInfoSerializer(serializers.Serializer):
    # get all products,count of products, max price
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()