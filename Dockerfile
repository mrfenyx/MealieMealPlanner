# Use the official slim Python 3.13 image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Default startup command
CMD ["python", "app.py"]