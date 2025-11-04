
FROM python:3.12-slim


# Create and switch to a working directory inside the container
WORKDIR /app

# Copy dependencies list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django project files into /app
COPY . .

# Run collectstatic automatically before starting Django
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Default commands
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
