import requests
from django.conf import settings
from ..base import BasePaymentProvider
from api.models import Payment

class SSLCommerzPaymentProvider(BasePaymentProvider):
    def create_payment(self, order):
        # 1. Prepare data for SSLCommerz
        post_data = {
            'store_id': settings.SSL_STORE_ID,
            'store_passwd': settings.SSL_STORE_PASS,
            'total_amount': order.total_amount,
            'currency': "BDT",
            'tran_id': f"txn_{order.id}", 
            'success_url': "http://localhost:8000/api/payments/ssl/callback/", 
            'fail_url': "http://localhost:8000/api/payments/ssl/callback/",
            'cancel_url': "http://localhost:8000/api/payments/ssl/callback/",
            'cus_name': "Customer Name",
            'cus_email': "cust@example.com",
            'cus_phone': "01711111111",
            'cus_add1': "Dhaka",
            'cus_city': "Dhaka",
            'cus_postcode': "1000",
            'cus_country': "Bangladesh",
            
            'shipping_method': "NO",
            'product_name': "Test Product",
            'product_category': "General",
            'product_profile': "general",
            
            # Optional: Force bKash if you want to skip selection page
            'multi_card_name': 'bkash' 
        }

        # 2. Send request to SSLCommerz
        if settings.SSL_IS_SANDBOX:
            url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
        else:
            url = "https://securepay.sslcommerz.com/gwprocess/v4/api.php"

        response = requests.post(url, data=post_data)
        data = response.json()

        if data.get('status') == 'SUCCESS':
            # 3. Store the Transaction ID locally
            Payment.objects.create(
                order=order,
                provider='sslcommerz',
                transaction_id=post_data['tran_id'],
                status='pending',
                amount=order.total_amount
            )
            # 4. Give the Gateway URL to the frontend
            return {'redirect_url': data['GatewayPageURL']}
        else:
            raise Exception(f"SSL Init Failed: {data.get('failedreason')}")

    def confirm_payment(self, payment_id, **kwargs):
        
        pass

    def query_payment(self, payment_id):
        pass
    
    def handle_webhook(self, request):
        pass