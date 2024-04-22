FROM python:3.9

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Install Daphne and Gunicorn
RUN pip install daphne gunicorn

# Install Twisted extras for HTTP/2 and TLS support
RUN pip install -U "Twisted[tls,http2]"

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project files into the container
COPY . /app/
