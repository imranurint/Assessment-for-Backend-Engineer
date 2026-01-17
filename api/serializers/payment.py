from rest_framework import serializers
from api.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source='order', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'provider', 'transaction_id', 'status', 'amount', 'created_at']
        read_only_fields = fields

class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(help_text="ID of the order to pay for")
    provider = serializers.ChoiceField(choices=[('stripe', 'Stripe'), ('stripe-checkout', 'Stripe Checkout'), ('bkash', 'bKash'), ('bkash-ssl', 'bKash (SSLCommerz)')], help_text="Payment provider slug")

class PaymentConfirmSerializer(serializers.Serializer):
    payment_id = serializers.CharField(help_text="Transaction ID or Session ID from provider")
    provider = serializers.ChoiceField(choices=[('stripe', 'Stripe'), ('stripe-checkout', 'Stripe Checkout'), ('bkash', 'bKash'), ('bkash-ssl', 'bKash (SSLCommerz)')], help_text="Payment provider slug")
