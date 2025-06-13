# Use official Playwright image with all browser deps
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Upgrade pip and install Python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Flask/Gunicorn port
EXPOSE 10000

# Run app with 1 worker + long timeout to avoid Render memory/SIGKILL issues
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers=1", "--threads=1", "--timeout=120"]

