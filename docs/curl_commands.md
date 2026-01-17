# E-commerce API cURL Commands

> **NOTE:** Ensure the server is running (`python manage.py runserver`) and you have valid credentials/keys in `.env`.

## Setup & Seeding

To populate the database with an Admin user and sample products:

```bash
python seed_data.py
```

**Admin Credentials:**
*   Email: `admin@example.com`
*   Password: `adminpassword123`

**Customer Credentials:**
*   Email: `customer@example.com`
*   Password: `password123`

## Authentication

### 1. Register (User)
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login (User or Admin)
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```
**Response:**
```json
{
    "refresh": "...",
    "access": "YOUR_ACCESS_TOKEN"
}
```
**Export the token for subsequent requests:**
```bash
export TOKEN="YOUR_ACCESS_TOKEN"
```
*(For admin operations, login as admin and export `ADMIN_TOKEN`)*

## Products & Categories

### 3. List Categories (Tree/All - Public)
```bash
curl -X GET http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json"
```

### 3.1 Create Category (Admin Only)
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Category",
    "slug": "new-category"
  }'
```

### 3.2 Update Category (Admin Only)
```bash
curl -X PATCH http://localhost:8000/api/categories/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Category"
  }'
```

### 3.3 Delete Category (Admin Only)
```bash
curl -X DELETE http://localhost:8000/api/categories/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4. List Products (Public)
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN"
```

### 4.1 Product Recommendations (DFS + Caching)
```bash
curl -X GET http://localhost:8000/api/products/recommendations/?category=1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 5. Create Product (Admin Only)
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "sku": "NEW_001",
    "description": "Admin created product",
    "price": "50.00",
    "stock": 100,
    "status": "active",
    "category": 1
  }'
```

### 6. Update Product (Admin Only)
```bash
curl -X PATCH http://localhost:8000/api/products/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": "45.00"
  }'
```

### 7. Delete Product (Admin Only)
```bash
curl -X DELETE http://localhost:8000/api/products/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Orders

### 8. Create Order
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
        {"product_id": 1, "quantity": 1}
    ]
  }'
```

### 9. Get User Orders
```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $TOKEN"
```

## Payments

### 10. Initiate Payment (Stripe - Client Side Flow)
This returns a `client_secret` for the frontend SDK.
```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "provider": "stripe"
  }'
```

### 10.1 Initiate Payment (Stripe Checkout - Redirect Flow)
This returns a `redirect_url` to a hosted Stripe page.
```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "provider": "stripe-checkout"
  }'
```

### 10.2 Initiate Payment (bKash via SSLCommerz - Redirect Flow)
This returns a `redirect_url` to the SSLCommerz gateway.
```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "provider": "bkash"
  }'
```

### 11. Confirm Payment (Manual/Stripe)
Used for the manual flow or client-sdk confirmation step if needed server-side.
```bash
curl -X POST http://localhost:8000/api/payments/confirm/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "PAYMENT_INTENT_ID_OR_TXN_ID",
    "provider": "stripe"
  }'
```

### 12. Get User Payments
```bash
curl -X GET http://localhost:8000/api/payments/ \
  -H "Authorization: Bearer $TOKEN"
```



## Webhooks

### 13. Stripe Webhook (Simulation)
```bash
curl -X POST http://localhost:8000/api/payments/webhook/stripe/ \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=123,v1=SIGNATURE" \
  -d '{
    "type": "payment_intent.succeeded",
    "data": {
      "object": {
        "id": "pi_12345",
        "status": "succeeded"
      }
    }
  }'
```
> Note: For the webhook to actually work with signature verification, you need to use the Stripe CLI to forward events to localhost, or disable signature verification temporarily in development.
