from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from api.models import Product
from api.serializers.product import ProductSerializer, ProductListSerializer
from api.services.category_service import CategoryService

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser] # Actually we need IsAdminUser for mutations.
    
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny] 
        return [permission() for permission in permission_classes]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        category_id = self.request.query_params.get('category')
        if category_id:
            try:
                # Use DFS to get all subcategories
                category_ids = CategoryService.get_descendants_ids(int(category_id))
                queryset = queryset.filter(category__id__in=category_ids)
            except ValueError:
                pass
                
        return queryset

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        Recommend products based on category hierarchy (Mock implementation: recent in category)
        """
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({"error": "Category ID required"}, status=400)
            
        category_ids = CategoryService.get_descendants_ids(int(category_id))
        products = Product.objects.filter(
            category__id__in=category_ids, 
            status='active'
        ).order_by('-created_at')[:10]
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
