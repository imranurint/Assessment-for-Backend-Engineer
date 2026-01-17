import requests
import json
from django.conf import settings
from api.payments.base import BasePaymentProvider
from api.models import Payment

class BkashPaymentProvider(BasePaymentProvider):
    def __init__(self):
        self.base_url = settings.BKASH_BASE_URL
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _get_token(self):
        url = f"{self.base_url}/tokenized/checkout/token/grant"
        payload = {
            "app_key": self.app_key,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload, headers={"username": self.username, "password": self.password})
        data = response.json()
        
        if 'id_token' in data:
            return data['id_token']
        raise Exception(f"Failed to get bKash token: {data}")

    def create_payment(self, order):
        token = self._get_token()
        url = f"{self.base_url}/tokenized/checkout/create"
        headers = self.headers.copy()
        headers['Authorization'] = token
        headers['X-APP-Key'] = self.app_key

        payload = {
            "mode": "0011",
            "payerReference": "01711111111", 
            "callbackURL": "http://localhost:8000/api/payments/bkash/callback", 
            "amount": str(order.total_amount),
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": f"Inv_{order.id}" 
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if 'paymentID' in data:
            Payment.objects.create(
                order=order,
                provider='bkash',
                transaction_id=data['paymentID'],
                status='pending',
                amount=order.total_amount,
                raw_response=data
            )
            return {
                'payment_id': data['paymentID'],
                'bkashURL': data['bkashURL']
            }
        else:
             raise Exception(f"bKash create failed: {data}")

    def confirm_payment(self, payment_id, **kwargs):
        token = self._get_token()
        url = f"{self.base_url}/tokenized/checkout/execute"
        headers = self.headers.copy()
        headers['Authorization'] = token
        headers['X-APP-Key'] = self.app_key
        
        payload = {"paymentID": payment_id}
        
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        payment = Payment.objects.get(transaction_id=payment_id)
        
        if data.get('statusCode') == '0000' and data.get('transactionStatus') == 'Completed':
            payment.status = 'success'
            payment.raw_response = data
            payment.save()
            
            payment.order.mark_as_paid()
            
            for item in payment.order.items.all():
                item.product.reduce_stock(item.quantity)
                
            return {'status': 'success', 'trxID': data['trxID']}
        else:
            payment.status = 'failed'
            payment.raw_response = data
            payment.save()
            return {'status': 'failed', 'message': data.get('statusMessage')}

    def query_payment(self, payment_id):
        pass

    def handle_webhook(self, request):
        pass
