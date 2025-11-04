# Use lightweight Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency file and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Command for both local & Render
CMD if [ "$DJANGO_ENV" = "production" ]; then \
    echo "🚀 Running migrations and starting Gunicorn..."; \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:8000; \
  else \
    echo "💻 Running Django dev server locally..."; \
    python manage.py runserver 0.0.0.0:8000; \
  fi
