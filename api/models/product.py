from django.db import models
from django.core.exceptions import ValidationError

class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    category = models.ForeignKey(
        'Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name

    def is_available(self):
        return self.status == 'active' and self.stock > 0

    def reduce_stock(self, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        if self.stock < quantity:
            raise ValidationError(f"Insufficient stock for product {self.sku}. Available: {self.stock}")
        
        self.stock -= quantity
        self.save()
