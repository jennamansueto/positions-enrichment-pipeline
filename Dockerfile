FROM apache/spark-py:v3.5.1

USER root

# Install uv for faster dependency management
RUN pip install uv

WORKDIR /app

# Copy dependency file first for caching
COPY pyproject.toml .
RUN uv pip install --system ".[dev]"

# Copy application code
COPY src/ src/
COPY config/ config/
COPY scripts/ scripts/

ENV PYTHONPATH=/app/src
ENV SPARK_HOME=/opt/spark
ENV WAREHOUSE_PATH=/data/warehouse

ENTRYPOINT ["python", "-m", "enterprise_pipeline"]
