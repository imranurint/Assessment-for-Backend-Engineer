# E-Commerce Ordering & Payment System API

A comprehensive Django REST Framework API for e-commerce with multi-provider payment integration (Stripe, bKash).

## Features
- **User Management**: JWT Authentication, Email-based login.
- **Product Management**: Hierarchical categories, stock management.
- **Order System**: Cart calculations, order status tracking.
- **Payment System**: Switchable Strategy Pattern for Stripe and bKash.
- **DFS & Caching**: Efficient category traversal using Depth-First Search and Redis.

## Setup

1. **Clone & Install Dependencies**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Environment Configuration**
    Copy `.env.example` to `.env` and fill in your credentials.
    ```bash
    cp .env.example .env
    ```

3. **Database**
    By default, SQLite is used for development. For Production, configure PostgreSQL in `.env`.
    
4. **Migrations**
    ```bash
    python manage.py makemigrations api
    python manage.py migrate
    ```

5. **Run Server**
    ```bash
    python manage.py runserver
    ```

## Documentation
The detailed technical documentation can be found in the `docs/` directory:
- [System Design & Architecture](docs/system_design.md)
- [API cURL Commands Guide](docs/curl_commands.md)
- [Interactive API UI (Swagger)](http://localhost:8000/api/docs/) (Requires server running)

## Redis Setup
Ensure Redis is running for category tree caching.
```bash
redis-server
```

## Testing
Run unit tests:
```bash
python manage.py test api
```
