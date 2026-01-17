from rest_framework import serializers
from django.db import transaction
from api.models import Order, OrderItem, Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_sku', 'quantity', 'price', 'subtotal')
        read_only_fields = ('price', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'user_email', 'total_amount', 'status', 'created_at', 'items')
        read_only_fields = ('user', 'total_amount', 'status', 'created_at')

class OrderCreateSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")
        
        product_ids = [item['product_id'] for item in items]
        products = Product.objects.in_bulk(product_ids)
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            
            if not product_id or not quantity:
                raise serializers.ValidationError("product_id and quantity are required.")
                
            if quantity <= 0:
                raise serializers.ValidationError(f"Quantity must be positive for product {product_id}.")
                
            product = products.get(product_id)
            if not product:
                raise serializers.ValidationError(f"Product {product_id} does not exist.")
                
            if not product.is_available():
                raise serializers.ValidationError(f"Product {product.name} is not available.")
                
            if product.stock < quantity:
                # Note: We check stock here but reduce it only after payment success as per requirement.
                # However, usually we should check if we can fulfill it now.
                raise serializers.ValidationError(f"Insufficient stock for {product.name}. Available: {product.stock}")
                
        return items

    def create(self, validated_data):
        items_data = validated_data['items']
        user = self.context['request'].user
        
        with transaction.atomic():
            order = Order.objects.create(user=user, status='pending')
            
            order_items = []
            for item in items_data:
                product = Product.objects.get(id=item['product_id'])
                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price, # Snapshot price
                    subtotal=product.price * item['quantity']
                )
                order_items.append(order_item)
            
            OrderItem.objects.bulk_create(order_items)
            
            # Calculate total using deterministic algorithm
            order.calculate_total()
            
        return order
