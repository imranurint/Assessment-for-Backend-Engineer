from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Order, Product, Payment, OrderItem

User = get_user_model()

class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='payer', email='payer@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(name='P1', sku='P1', price=100, stock=10)
        self.order = Order.objects.create(user=self.user, status='pending', total_amount=100)
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=100, subtotal=100)

    @patch('api.payments.stripe_provider.stripe.PaymentIntent.create')
    def test_initiate_stripe_payment(self, mock_create):
        mock_intent = MagicMock(id='pi_123', client_secret='secret_123', status='pending')
        mock_create.return_value = mock_intent
        
        url = reverse('payment-initiate')
        data = {'order_id': self.order.id, 'provider': 'stripe'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['transaction_id'], 'pi_123')
        
        # Verify DB
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.provider, 'stripe')
        self.assertEqual(payment.status, 'pending')

    @patch('api.payments.bkash_provider.requests.post')
    def test_initiate_bkash_payment(self, mock_post):
        # Mock token grant and create payment
        # This is tricky because requests.post is called twice. Sideloading responses...
        
        mock_token_resp = MagicMock()
        mock_token_resp.json.return_value = {'id_token': 'token123'}
        
        mock_create_resp = MagicMock()
        mock_create_resp.json.return_value = {'paymentID': 'bkash_123', 'bkashURL': 'http://bkash.com'}
        
        # Side effect to return different responses
        mock_post.side_effect = [mock_token_resp, mock_create_resp]
        
        url = reverse('payment-initiate')
        data = {'order_id': self.order.id, 'provider': 'bkash'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_id'], 'bkash_123')
