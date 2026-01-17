from rest_framework import views, response, permissions, status
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from api.models import Order, Payment
from api.payments.factory import PaymentFactory

from drf_spectacular.utils import extend_schema
from api.serializers.payment import PaymentSerializer, PaymentInitiateSerializer, PaymentConfirmSerializer

class InitiatePaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=PaymentInitiateSerializer, responses={200: dict})
    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        order_id = serializer.validated_data['order_id']
        provider_name = serializer.validated_data['provider']
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if order.status != 'pending':
            return response.Response(
                {"error": "Order is not in pending state"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            provider = PaymentFactory.get_provider(provider_name)
            data = provider.create_payment(order)
            return response.Response(data)
        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmPaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=PaymentConfirmSerializer, responses={200: dict})
    def post(self, request):
        serializer = PaymentConfirmSerializer(data=request.data)
        if not serializer.is_valid():
             return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
             
        payment_id = serializer.validated_data['payment_id']
        provider_name = serializer.validated_data['provider']
        
        try:
            provider = PaymentFactory.get_provider(provider_name)
            result = provider.confirm_payment(payment_id)
            return response.Response(result)
        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from drf_spectacular.types import OpenApiTypes

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT}, description="Endpoint for Stripe to send webhook events (e.g. payment_intent.succeeded)")
    def post(self, request):
        try:
            provider = PaymentFactory.get_provider('stripe')
            provider.handle_webhook(request)
            return response.Response({"status": "received"})
        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from api.serializers.payment import PaymentSerializer

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).order_by('-created_at')

