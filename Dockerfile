

FROM python:3.13-slim

# Create non-root user with high UID
RUN useradd --create-home --shell /bin/bash --uid 10000 app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app ./app .
USER app

EXPOSE 5000
# ENV FLASK_APP=./app/app.py
# ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
ENTRYPOINT ["python", "app.py"]