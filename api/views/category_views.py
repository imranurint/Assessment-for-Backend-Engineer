from rest_framework import viewsets, views, response, permissions
from api.models import Category
from api.serializers.category import CategorySerializer
from api.services.category_service import CategoryService

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny] 
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        CategoryService.invalidate_cache()
        serializer.save()

    def perform_update(self, serializer):
        CategoryService.invalidate_cache()
        serializer.save()

    def perform_destroy(self, instance):
        CategoryService.invalidate_cache()
        instance.delete()

class CategoryTreeView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tree = CategoryService.get_cached_tree()
        return response.Response(tree)
