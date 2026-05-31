FROM python:3.11-slim

# Install Java (required for PySpark/Spark runtime)
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/lib/jvm/java-21-openjdk-$(dpkg --print-architecture) /usr/lib/jvm/java-21-openjdk

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency file first for caching
COPY pyproject.toml .
RUN uv pip install --system ".[dev]"

# Copy application code
COPY src/ src/
COPY config/ config/
COPY scripts/ scripts/

ENV PYTHONPATH=/app/src
ENV WAREHOUSE_PATH=/data/warehouse

ENTRYPOINT ["python", "-m", "enterprise_pipeline"]
