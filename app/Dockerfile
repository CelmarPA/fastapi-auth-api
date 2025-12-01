########## BASE ##########
FROM python:3.12-slim AS base

# Avoid bugs with Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# App directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -f /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Port used by the Render
EXPOSE 8000

########## RUN ##########
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
