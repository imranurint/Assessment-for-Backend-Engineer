from rest_framework import serializers
from api.models import Category

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'children')

    def get_children(self, obj):
        # This approach causes N+1 queries if used in a list view without prefetching.
        # For efficiency, we should rely on the Service's cached tree structure in the view,
        # but for individual detail view this is acceptable.
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

class CategoryTreeSerializer(serializers.Serializer):
    """
    Serializer for the cached tree structure (dicts, not model instances).
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    children = serializers.JSONField()
    # Since we can't easily add dependencies like drf-recursive without confirming,
    # we'll use a simpler approach or just `serializers.JSONField` for the tree
    # or implement `get_children` manually.
    
    # Simple recursive Approach:
    def to_representation(self, value):
        return value
