# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000


# Run entrypoint script 
CMD ["sh", "-c", "while ! nc -z db 5432; do sleep 1; done; python manage.py migrate && gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:8000"]
