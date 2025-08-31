# --- Builder ---
# Build the environment with all the necessary tools
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Installs all system dependencies (build and runtime)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    postgresql-client \
    curl \
    tesseract-ocr tesseract-ocr-por libtesseract-dev libleptonica-dev \
    libjpeg-dev libpng-dev libwebp-dev \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create an isolated virtual environment
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (using the production version)
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt # ATENÇÃO: Usar production.txt

# --- Runner ---
# The final image, streamlined and ready for production
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install ONLY the runtime dependencies (not the build ones)
RUN apt-get update && apt-get install -y \
    libpq5 \
    tesseract-ocr tesseract-ocr-por \
    libjpeg62-turbo libpng16-16 libwebp7 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create user and working directory
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the virtual environment with the dependencies already installed from the builder stage.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Creates directories and sets permissions
RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /app/media /app/staticfiles /app/logs && \
    chown -R appuser:appuser /app

# Sets up the user to run the application
USER appuser

# Export door
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
