from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name
    
    def get_descendants(self):
        """
        Get all descendants using DFS or recursive query.
        For simple usage, we might just return children, but service layer handles full DFS.
        """
        children = list(self.children.all())
        descendants = children.copy()
        for child in children:
            descendants.extend(child.get_descendants())
        return descendants
