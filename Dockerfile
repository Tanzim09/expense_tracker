
FROM python:3.12-slim


# Create and switch to a working directory inside the container
WORKDIR /app

# Copy dependencies list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django project files into /app
COPY . .

# Collect static files (for production)
RUN python manage.py collectstatic --noinput || true

# Expose port 8000
EXPOSE 8000

# Default commands
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Command for both local & Render
CMD if [ "$DJANGO_ENV" = "production" ]; then \
    echo " Starting Gunicorn for Render..."; \
    gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:8000; \
  else \
    echo " Starting Django dev server..."; \
    python manage.py runserver 0.0.0.0:8000; \
  fi
