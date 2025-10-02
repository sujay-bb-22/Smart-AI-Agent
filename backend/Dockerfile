FROM python:3.11-slim

WORKDIR /app

# Copy requirements from the backend folder and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code from the backend folder
COPY backend/ .

# Make start script executable
RUN chmod +x start.sh

# Set the startup command
CMD ["./start.sh"]
