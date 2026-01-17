# Environment Configuration Guide

This guide details how to configure the e-commerce system for local development and production.

## 1. Environment Variables (`.env`)

Create a `.env` file in the project root.

| Variable | Description | Required | Default/Example |
|----------|-------------|----------|-----------------|
| `DEBUG` | Enable debug mode | No | `False` (Prod), `True` (Dev) |
| `SECRET_KEY` | Django secret key | Yes | `django-insecure-...` |
| `ALLOWED_HOSTS` | Comma-separated hosts | No | `localhost,127.0.0.1` |

### Database Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME` | Database name | `postgres` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `localhost` or `db` (docker) |
| `DB_PORT` | Database port | `5432` |

### Payment Providers
| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Stripe Secret Key from Dashboard |
| `STRIPE_PUBLISHABLE_KEY` | Stripe Public Key from Dashboard |
| `STRIPE_WEBHOOK_SECRET` | Secret for verifying webhooks `whsec_...` |
| `BKASH_APP_KEY` | bKash App Key |
| `BKASH_APP_SECRET` | bKash App Secret |
| `BKASH_USERNAME` | bKash Merchant Username |
| `BKASH_PASSWORD` | bKash Merchant Password |
| `BKASH_BASE_URL` | Sandbox: `https://tokenized.sandbox.bka.sh/v1.2.0-beta` |

### Redis (Caching)
| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Redis Connection URL | `redis://127.0.0.1:6379/1` |

---

## 2. Docker Deployment

### Prerequisites
- Docker Engine
- Docker Compose

### Setup Steps

1.  **Configure Environment**
    Ensure your `.env` file is set up. For Docker, `DB_HOST` should be `db` and `REDIS_URL` should be `redis://redis:6379/1`. The `docker-compose.yml` overrides these automatically for convenience, but you can set them manually in `.env` if preferred.

2.  **Build and Run**
    ```bash
    docker-compose up --build -d
    ```
    This will:
    - Build the Django image
    - Start PostgreSQL container (port 5433)
    - Start Redis container (port 6380)
    - Start Django Gunicorn server (port 8000)

3.  **Run Migrations**
    The `command` in `docker-compose.yml` runs migrations automatically on startup.
    To run manual commands:
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

4.  **Access**
    - API: `http://localhost:8000/api/`
    - Swagger Docs: `http://localhost:8000/api/docs/`

5.  **Shutdown**
    ```bash
    docker-compose down
    # To remove volumes (reset DB):
    # docker-compose down -v
    ```

### Production Notes
- Set `DEBUG=False`.
- Update `ALLOWED_HOSTS` with your domain.
- Use a robust secret key.
- Configure SSL/TLS (e.g., using Nginx as a reverse proxy in front of Gunicorn).
