import stripe
from django.conf import settings
from api.payments.base import BasePaymentProvider
from api.models import Payment

class StripeCheckoutProvider(BasePaymentProvider):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment(self, order):
        # Create a Checkout Session
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Order #{order.id}',
                    },
                    'unit_amount': int(order.total_amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/api/payments/stripe/success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/api/payments/stripe/cancel/',
            metadata={'order_id': order.id},
        )
        
        Payment.objects.create(
            order=order,
            provider='stripe-checkout',
            transaction_id=session.id,
            status='pending',
            amount=order.total_amount
        )
        
        # Return the Redirect URL
        return {'redirect_url': session.url}

    def confirm_payment(self, payment_id, **kwargs):
        
        session = stripe.checkout.Session.retrieve(payment_id)
        if session.payment_status == 'paid':
             self._process_success_session(session)
             return {'status': 'success'}
        return {'status': session.payment_status}

    def query_payment(self, payment_id):
        session = stripe.checkout.Session.retrieve(payment_id)
        return {'status': session.payment_status}

    def handle_webhook(self, request):
        pass 

    def _process_success_session(self, session):
        try:
            payment = Payment.objects.get(transaction_id=session.id)
            if payment.status == 'success':
                return
            
            payment.status = 'success'
            payment.raw_response = str(session)
            payment.save()
            
            payment.order.mark_as_paid()
            for item in payment.order.items.all():
                item.product.reduce_stock(item.quantity)
                
        except Payment.DoesNotExist:
            pass
