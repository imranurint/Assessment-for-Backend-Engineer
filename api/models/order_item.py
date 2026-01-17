from django.db import models

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.PROTECT) # Prevent deletion of product if in order
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Snapshot price
    subtotal = models.DecimalField(max_digits=12, decimal_places=2) 

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
