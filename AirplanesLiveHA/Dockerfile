# AirplanesLiveHA/Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the necessary files
COPY . .

# Install dependencies
RUN pip install flask requests

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]