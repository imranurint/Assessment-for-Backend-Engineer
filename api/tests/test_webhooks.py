from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Order, Payment, Product, OrderItem, User

class WebhookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='webhookuser', email='webhook@example.com', password='pw')
        self.product = Product.objects.create(name='WebProd', sku='WP1', price=100, stock=10)
        self.order = Order.objects.create(user=self.user, status='pending', total_amount=100)
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=100, subtotal=100)
        
        self.payment = Payment.objects.create(
            order=self.order,
            provider='stripe',
            transaction_id='pi_test_123',
            status='pending',
            amount=100
        )

    @patch('api.payments.stripe_provider.stripe.Webhook.construct_event')
    def test_stripe_webhook_success(self, mock_construct_event):
        # Mock the Stripe event object
        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': MagicMock(id='pi_test_123', status='succeeded')
            }
        }
        mock_construct_event.return_value = mock_event
        
        url = reverse('stripe-webhook')
        # DRF test client handles json nicely but webhook is raw body usually.
        # However, our view parses it via Stripe SDK which reads body.
        # But `stripe.Webhook.construct_event` takes payload. 
        # In test, we mock `construct_event`, so payload content matters less as long as we pass signature.
        
        response = self.client.post(
            url, 
            data={'id': 'evt_123'}, 
            format='json',
            HTTP_STRIPE_SIGNATURE='valid_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        # Verify payment updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'success')
        
        # Verify order updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
        
        # Verify stock reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

    @patch('api.payments.stripe_provider.stripe.Webhook.construct_event')
    def test_stripe_webhook_failure(self, mock_construct_event):
        mock_event = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': MagicMock(id='pi_test_123', status='failed')
            }
        }
        mock_construct_event.return_value = mock_event
        
        url = reverse('stripe-webhook')
        self.client.post(url, {}, HTTP_STRIPE_SIGNATURE='sig')
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
