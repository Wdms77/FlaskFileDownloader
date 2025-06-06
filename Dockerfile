FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash appuser

WORKDIR /app

COPY --chown=appuser:appuser requirements.txt run.py /app/
COPY --chown=appuser:appuser app /app/app
COPY --chown=appuser:appuser tests /app/tests

RUN mkdir -p /logs /data && chown -R appuser:appuser /app /data /logs

RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

VOLUME ["/data"]

EXPOSE 5000

USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-k", "gevent", "app:create_app()"]