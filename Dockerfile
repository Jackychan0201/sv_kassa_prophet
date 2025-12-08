# Use official Python image
FROM python:3.10-slim

# Install system dependencies needed to build prophet
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    gcc \
    git \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Copy the requirements first to leverage Docker cache
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy app
COPY . /app

# Expose port (Render/Cloud Run will set the port; Uvicorn will read PORT env)
ENV PORT 8000

# Use uvicorn (production deployments may want Gunicorn+Uvicorn workers)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
