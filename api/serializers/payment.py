from rest_framework import serializers
from api.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source='order', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'provider', 'transaction_id', 'status', 'amount', 'created_at']
        read_only_fields = fields
