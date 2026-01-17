from rest_framework import serializers
from api.models import Product
from api.serializers.category import CategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'sku', 'description', 'price', 
            'stock', 'status', 'category', 'category_detail',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'sku', 'price', 'stock', 'status', 'category_name')
