from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Product, Category, Order

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='orderuser', email='user@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='General', slug='general')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST1',
            price=100.00,
            stock=50,
            category=self.category
        )

    def test_create_order(self):
        url = reverse('order-list')
        data = {
            'items': [
                {'product_id': self.product.id, 'quantity': 2}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.total_amount, 200.00)
        self.assertEqual(order.status, 'pending')

    def test_order_stock_validation(self):
        url = reverse('order-list')
        data = {
            'items': [
                {'product_id': self.product.id, 'quantity': 51} # Exceeds 50
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient stock', str(response.data))
