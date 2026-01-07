# Multi-stage build for lightweight Python Flask app
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app.py .
COPY charm_calculator.py .
COPY charm_spells_data.py .
COPY templates/ templates/
COPY static/ static/

# Create data directory (optional, for spell file)
RUN mkdir -p data

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Make sure scripts are in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=2)"

# Run the application with gunicorn for production
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

