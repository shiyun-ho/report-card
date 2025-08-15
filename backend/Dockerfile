FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libfontconfig1 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgirepository-1.0-1 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy project files for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Add uv to PATH for appuser
ENV PATH="/root/.local/bin:$PATH"

# Set Python path to include src directory
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Expose port
EXPOSE 8000

# Default command using uv run
CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]