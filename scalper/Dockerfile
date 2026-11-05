# Scalper DEMO image. Build context = repo root (see /railway.json) or this folder (Docker/VPS).
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 DATA_DIR=/data PORT=8080 TZ=America/Mexico_City
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY bot /app/bot
COPY config.yaml /app/config.yaml
RUN useradd -m bot && mkdir -p /data && chown bot /data
USER bot
VOLUME ["/data"]
EXPOSE 8080
HEALTHCHECK --interval=60s --timeout=10s --start-period=120s CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8080')+'/health',timeout=8)"
CMD ["python", "-m", "bot"]
