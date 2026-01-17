from django.db import models

class Payment(models.Model):
    PROVIDER_CHOICES = (
        ('stripe', 'Stripe'),
        ('bkash', 'bKash'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    raw_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.provider} - {self.order.id} - {self.status}"
