import stripe
from rest_framework.views import APIView
from rest_framework import permissions
from django.conf import settings
from django.http import HttpResponse
from api.models import Payment

class StripeSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        session_id = request.GET.get('session_id')
        if not session_id:
             return HttpResponse("Missing Session ID", status=400)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                try:
                    # We stored session.id as transaction_id
                    payment = Payment.objects.get(transaction_id=session.id)
                    
                    if payment.status != 'success':
                        payment.status = 'success'
                        payment.raw_response = str(session)
                        payment.save()
                        
                        payment.order.mark_as_paid()
                        for item in payment.order.items.all():
                            item.product.reduce_stock(item.quantity)
                        
                    return HttpResponse("Payment Successful! Order Confirmed.")
                except Payment.DoesNotExist:
                    return HttpResponse("Payment record not found.", status=404)
            else:
                return HttpResponse("Payment not paid.", status=400)

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

class StripeCancelView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return HttpResponse("Payment Canceled.")
