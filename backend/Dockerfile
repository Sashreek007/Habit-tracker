# Using a light version of Python image
FROM python:3.10-slim

# Install required system dependencies for psycopg2 (NOT binary)
RUN apt-get update && apt-get install -y \
  gcc \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Set working directory in the image
WORKDIR /app

# Copy all the backend files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]

