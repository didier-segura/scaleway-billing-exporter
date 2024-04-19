# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the maintainer
LABEL maintainer="Didier SEGURA <contact@didier-segura.Fr>"

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script into the container
COPY main.py .

# Update and upgrade packages for security
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install requests prometheus_client

# Run the Python script when the container starts
CMD ["python", "main.py"]
