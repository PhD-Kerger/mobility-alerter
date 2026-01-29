# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY alerter/ ./alerter/
COPY log_collector/ ./log_collector/
COPY main.py .
COPY utils/ ./utils/

# Command to run the application
CMD ["python", "main.py"]