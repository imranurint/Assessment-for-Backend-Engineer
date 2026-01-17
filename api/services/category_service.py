from django.core.cache import cache
from api.models import Category

class CategoryService:
    CACHE_KEY = 'category_tree_structure'
    CACHE_TIMEOUT = 3600  # 1 hour

    @classmethod
    def get_cached_tree(cls):
        """
        Retrieve the category tree from cache or build it.
        """
        tree = cache.get(cls.CACHE_KEY)
        if not tree:
            tree = cls.build_tree()
            cache.set(cls.CACHE_KEY, tree, cls.CACHE_TIMEOUT)
        return tree

    @classmethod
    def build_tree(cls):
        """
        Builds a nested dictionary structure of categories.
        Root categories (parent=None) are at the top level.
        """
        # Optimized: Fetch all categories in one query
        categories = Category.objects.all().order_by('name')
        category_map = {cat.id: {'id': cat.id, 'name': cat.name, 'slug': cat.slug, 'children': []} for cat in categories}
        roots = []

        for cat in categories:
            if cat.parent_id:
                parent = category_map.get(cat.parent_id)
                if parent:
                    parent['children'].append(category_map[cat.id])
            else:
                roots.append(category_map[cat.id])
        
        return roots

    @classmethod
    def get_descendants_ids(cls, category_id):
        """
        DFS traversal to get all descendant IDs for a given category.
        Useful for product filtering.
        """
        # We can implement a fresh DFS here or use the cached tree.
        # Implemented as fresh DFS for demonstration of algorithm requirement on DB/Model,
        # but using cache is better for performance.
        # Let's use the cached tree to find the node and then DFS traverse it.
        
        tree = cls.get_cached_tree()
        node = cls._find_node(tree, category_id)
        
        if not node:
            return [category_id] # Just the category itself if found or fallback

        ids = [category_id]
        stack = [node]
        
        while stack:
            current = stack.pop()
            for child in current['children']:
                ids.append(child['id'])
                stack.append(child)
                
        return ids

    @classmethod
    def _find_node(cls, nodes, category_id):
        """
        Helper to find a node in the tree list.
        """
        for node in nodes:
            if node['id'] == category_id:
                return node
            
            found = cls._find_node(node['children'], category_id)
            if found:
                return found
        return None

    @classmethod
    def invalidate_cache(cls):
        cache.delete(cls.CACHE_KEY)
