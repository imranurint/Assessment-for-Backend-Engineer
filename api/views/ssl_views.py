from rest_framework.views import APIView
from rest_framework import permissions
from django.shortcuts import redirect
from django.http import HttpResponse
from api.models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class SSLPaymentCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.POST
        status = data.get('status')
        tran_id = data.get('tran_id')
        val_id = data.get('val_id')

        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            
            if status == 'VALID':
                payment.status = 'success'
                payment.raw_response = dict(data)
                payment.save()
                
                # Update Order
                payment.order.mark_as_paid()
                for item in payment.order.items.all():
                    item.product.reduce_stock(item.quantity)
                
                return HttpResponse("Payment Successful")
            else:
                payment.status = 'failed'
                payment.save()
                return HttpResponse("Payment Failed")
                
        except Payment.DoesNotExist:
            return HttpResponse("Invalid Transaction ID", status=400)
