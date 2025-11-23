# Quick Start Guide

## Prerequisites Check

```bash
docker --version          # >= 20.10
docker-compose --version  # >= 1.29
node --version           # >= 16
python3 --version        # >= 3.9
git --version
```

## 1. Clone & Setup

```bash
git clone <your-repo>
cd automation-system

# Create directory structure
mkdir -p dags agents/device_agent agents/ui_agent ui_tests
mkdir -p agents/device_agent/logs agents/ui_agent/test-results
```

## 2. Initialize Agents

### Device Agent (Python)

```bash
cd agents/device_agent

# Create requirements.txt
cat > requirements.txt << 'EOF'
requests==2.31.0
pika==1.3.2
python-dotenv==1.0.0
structlog==23.2.0
tenacity==8.2.3
EOF

# Create .env
cat > .env << 'EOF'
DOMOTICZ_URL=http://domoticz:8080
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
LOG_LEVEL=INFO
EOF
```

### UI Agent (Node.js)

```bash
cd agents/ui_agent
npm init -y
npm install --save-dev @playwright/test
npm install amqplib dotenv
```

## 3. Start Services

```bash
# From project root
docker-compose up -d

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f rabbitmq
docker-compose logs -f airflow-webserver
docker-compose logs -f device-agent
```

## 4. Access UIs

- **RabbitMQ Management:** http://localhost:15672 (guest/guest)
- **Airflow:** http://localhost:8080 (airflow/airflow)

## 5. Test Messaging

```bash
# Send test device command
python3 << 'EOF'
import pika
import json

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()
channel.exchange_declare(exchange='home', exchange_type='topic', durable=True)

message = {'idx': 1, 'action': 'On', 'correlation_id': 'test-123'}
channel.basic_publish(exchange='home', routing_key='device.1.cmd', body=json.dumps(message))
print("✓ Message sent")
connection.close()
EOF
```

## 6. Deploy First DAG

```bash
# Copy DAG to Airflow
cp dags/device_automation_dag.py $(docker inspect --format='{{.Mounts}}' automation-airflow-web | grep dags)

# Trigger in Airflow UI or via API
curl -X POST http://localhost:8080/api/v1/dags/device_automation_dag/dagRuns \
  -H "Content-Type: application/json" \
  -d '{"conf": {}}'
```

## 7. Run Playwright Tests

```bash
# Build and run tests
docker-compose run --rm ui-agent npm test

# View results
open agents/ui_agent/test-results/html/index.html
```

## 8. Stop Services

```bash
docker-compose down
docker-compose down -v  # Remove volumes too
```

## Common Commands

```bash
# View specific service logs
docker-compose logs device-agent -f

# Execute command in container
docker-compose exec device-agent python agent.py

# Rebuild image
docker-compose build device-agent

# Scale service
docker-compose up -d --scale device-agent=2

# Remove all containers and volumes
docker-compose down -v
```

## Troubleshooting

### RabbitMQ Connection Refused
```bash
# Check if RabbitMQ is running
docker-compose ps rabbitmq

# Restart RabbitMQ
docker-compose restart rabbitmq

# Check logs
docker-compose logs rabbitmq
```

### Airflow DAG Not Appearing
```bash
# Verify DAG file syntax
python -m py_compile dags/device_automation_dag.py

# Check Airflow logs
docker-compose logs airflow-scheduler

# Force DAG refresh
docker-compose exec airflow-webserver airflow dags list
```

### Device Agent Not Receiving Messages
```bash
# Check RabbitMQ queues
docker-compose exec rabbitmq rabbitmqctl list_queues

# Check agent logs
docker-compose logs device-agent

# Verify Domoticz connectivity
curl http://localhost:8081/json.htm?type=devices&rid=0
```

## Next Steps

1. **Implement Device Agent** - Copy agent.py template to agents/device_agent/
2. **Create Playwright Tests** - Add test files to agents/ui_agent/tests/
3. **Configure Domoticz** - Set up devices and note their IDs
4. **Create Jenkinsfile** - Set up CI/CD pipeline
5. **Deploy to Production** - Use Kubernetes or cloud deployment

## Documentation Files

- `IMPLEMENTATION_PLAN.md` - Detailed 11-phase implementation roadmap
- `TECHNICAL_SPECS.md` - Code templates and specifications
- `DOCKER_COMPOSE.yml` - Complete service configuration
- `Jenkinsfile` - CI/CD pipeline definition
