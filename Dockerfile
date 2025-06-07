
# ---------- Stage 1: Base ----------
FROM python:3.13-slim AS base
# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 10000 app
WORKDIR /app
ENV PYTHONPATH=/app


ARG ENVIRONMENT=production

COPY requirements.txt requirements.txt
COPY requirements-test.txt requirements-test.txt

RUN if [ "$ENVIRONMENT" = "test" ]; then \
        pip install --no-cache-dir -r requirements-test.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

COPY --chown=app:app ./app .

USER app

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# ---------- Stage 2: Test ----------
FROM base AS test
CMD ["pytest", "tests/unit"]

# ---------- Stage 3: Production ----------
FROM base AS production
CMD ["flask", "run"]
