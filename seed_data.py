import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from api.models import Product, Category

from api.models import Product, Category, User
from django.contrib.auth import get_user_model

User = get_user_model()

def seed():
    # 1. Create Superuser
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpassword123',
            first_name='Admin',
            last_name='User'
        )
        print("Seeded Superuser: admin@example.com / adminpassword123")
    else:
        print("Superuser already exists")

    # 1.5 Create Customer User
    if not User.objects.filter(email='customer@example.com').exists():
        User.objects.create_user(
            username='customer',
            email='customer@example.com', 
            password='password123',
            first_name='Customer',
            last_name='User'
        )
        print("Seeded Customer: customer@example.com / password123")
    else:
        print("Customer user already exists")

    # 2. Categories
    cat_elec, _ = Category.objects.get_or_create(name="Electronics", slug="electronics")
    cat_cloth, _ = Category.objects.get_or_create(name="Clothing", slug="clothing")
    
    # 3. Products
    products = [
        {
            "name": "Test Phone",
            "sku": "PHONE_001",
            "description": "A high-end smartphone",
            "price": Decimal("999.00"),
            "stock": 50,
            "status": "active",
            "category": cat_elec
        },
        {
            "name": "Laptop",
            "sku": "LAPTOP_001",
            "description": "Powerful laptop for devs",
            "price": Decimal("1500.00"),
            "stock": 20,
            "status": "active",
            "category": cat_elec
        },
        {
            "name": "T-Shirt",
            "sku": "TSHIRT_001",
            "description": "Cotton T-Shirt",
            "price": Decimal("25.00"),
            "stock": 100,
            "status": "active",
            "category": cat_cloth
        }
    ]

    for p_data in products:
        if not Product.objects.filter(sku=p_data['sku']).exists():
            Product.objects.create(**p_data)
            print(f"Seeded Product: {p_data['name']}")
        else:
            print(f"Product {p_data['name']} already exists")

if __name__ == '__main__':
    seed()
