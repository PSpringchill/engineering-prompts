FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY researcher_agent.py creator_agent.py scheduler_agent.py ./
COPY .env* ./

RUN mkdir -p /app/logs

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pika; pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))" || exit 1

CMD ["python", "-u", "researcher_agent.py"]
