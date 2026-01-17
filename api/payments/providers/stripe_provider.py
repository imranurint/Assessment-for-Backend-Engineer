import stripe
from django.conf import settings
from api.payments.base import BasePaymentProvider
from api.models import Payment

class StripePaymentProvider(BasePaymentProvider):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment(self, order):
        # Create PaymentIntent with amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100), # Amount in cents
            currency='usd', # Configurable
            metadata={'order_id': order.id},
            automatic_payment_methods={'enabled': True},
        )
        
        # Record pending payment
        raw_resp = {
            'id': intent.id, 
            'client_secret': intent.client_secret,
            'status': getattr(intent, 'status', 'pending')
        }
        Payment.objects.create(
            order=order,
            provider='stripe',
            transaction_id=intent.id,
            status='pending',
            amount=order.total_amount,
            raw_response=raw_resp
        )
        
        return {
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'transaction_id': intent.id
        }

    def confirm_payment(self, payment_id, **kwargs):
        # Logic to manually confirm if needed, or just refresh status
        intent = stripe.PaymentIntent.retrieve(payment_id)
        
        if intent.status == 'requires_payment_method':
            intent = stripe.PaymentIntent.modify(
                payment_id,
                payment_method='pm_card_visa',
            )
        
        if intent.status == 'requires_confirmation':
            intent = stripe.PaymentIntent.confirm(
                payment_id,
                return_url='http://localhost:8000/payment/callback' 
            )

        if intent.status == 'succeeded':
            self._process_success(intent)
            return {'status': 'success'}
        
        return {'status': intent.status}

    def query_payment(self, payment_id):
        intent = stripe.PaymentIntent.retrieve(payment_id)
        return {
            'status': intent.status, 
            'amount_received': intent.amount_received
        }

    def handle_webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise Exception("Invalid signature")

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._process_success(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._process_failure(payment_intent)
            
        return {'status': 'handled'}

    def _process_success(self, intent):
        try:
            payment = Payment.objects.get(transaction_id=intent.id)
            if payment.status == 'success':
                return

            payment.status = 'success'
            payment.raw_response = {
                'id': intent.id,
                'status': getattr(intent, 'status', 'succeeded')
            }
            payment.save()
            
            payment.order.mark_as_paid()
            
            for item in payment.order.items.all():
                item.product.reduce_stock(item.quantity)
        except Payment.DoesNotExist:
            pass

    def _process_failure(self, intent):
        try:
            payment = Payment.objects.get(transaction_id=intent.id)
            payment.status = 'failed'
            payment.raw_response = {
                'id': intent.id,
                'status': getattr(intent, 'status', 'failed')
            }
            payment.save()
        except Payment.DoesNotExist:
            pass
