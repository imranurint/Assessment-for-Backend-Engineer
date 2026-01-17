from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Category, Product, Order, OrderItem

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Laptop',
            sku='LPT123',
            description='A fast laptop',
            price=1000.00,
            stock=10,
            status='active',
            category=self.category
        )

    def test_product_stock_reduction(self):
        self.product.reduce_stock(2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

    def test_order_total_calculation(self):
        order = Order.objects.create(user=self.user, status='pending')
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price, # 1000.00
            subtotal=2000.00
        )
        
        # Add another item
        product2 = Product.objects.create(
            name='Mouse',
            sku='MSE123',
            price=50.00,
            stock=100,
            category=self.category
        )
        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=1,
            price=50.00,
            subtotal=50.00
        )
        
        order.calculate_total()
        self.assertEqual(order.total_amount, 2050.00)

    def test_category_hierarchy(self):
        sub_cat = Category.objects.create(name='Laptops', slug='laptops', parent=self.category)
        
        # Test get_descendants (simple version from model)
        descendants = self.category.get_descendants()
        self.assertIn(sub_cat, descendants)
        self.assertEqual(sub_cat.parent, self.category)
