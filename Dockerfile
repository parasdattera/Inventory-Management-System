# Backend image for the Inventory Management System (Django + gunicorn)
FROM python:3.12-slim

# - PYTHONDONTWRITEBYTECODE: don't write .pyc files
# - PYTHONUNBUFFERED: send logs straight to the terminal (good for docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached when only code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project.
COPY . .

# Collect static files (admin CSS, etc.) so WhiteNoise can serve them.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Apply database migrations, then start the app with gunicorn.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn inventory_system.wsgi:application --bind 0.0.0.0:8000"]
