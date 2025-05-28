
# FROM python:3.13-slim
# # Create non-root user with high UID
# RUN useradd --create-home --shell /bin/bash --uid 10000 app
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY --chown=app:app ./app .
# USER app
# EXPOSE 5000
# ENV FLASK_APP=app.py
# ENTRYPOINT ["flask", "--app", "app", "run", "--host=0.0.0.0"]


# ---------- Stage 1: Base ----------
FROM python:3.13-slim AS base

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 10000 app

WORKDIR /app

# Set ARG to define environment (prod/test)
ARG ENVIRONMENT=production

# Copy proper requirements file based on ENVIRONMENT
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
ARG ENVIRONMENT=test
COPY --from=base /app /app
# COPY ./tests ./tests

CMD ["pytest", "tests"]

# ---------- Stage 3: Production ----------
FROM base AS production
ARG ENVIRONMENT=production
COPY --from=base /app /app
CMD ["flask", "run"]
