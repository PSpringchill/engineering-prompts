# Multi-Agent Automation System Implementation Plan

## Overview
A production-ready system integrating Playwright, Domoticz, Apache Airflow, and Jenkins with real-time messaging, containerization, and CI/CD automation.

---

## Phase 0: Prerequisites & Validation

### Environment Checklist
- [ ] Linux server/VM or Kubernetes cluster
- [ ] Docker & Docker Compose (v20.10+)
- [ ] Git installed
- [ ] Node.js >= 16 & npm
- [ ] Python >= 3.9
- [ ] Jenkins server accessible
- [ ] Domoticz server accessible
- [ ] Container registry access (DockerHub/GitHub/private)

### Validation Commands
```bash
docker --version
docker-compose --version
node --version
python3 --version
git --version
```

---

## Phase 1: Core Infrastructure Setup

### 1.1 Message Broker (RabbitMQ)

**Deliverable:** RabbitMQ running with management console

**Steps:**
1. Create `docker-compose.yml` with RabbitMQ service
2. Enable management plugin (port 15672)
3. Set default credentials (guest/guest for dev, change for prod)
4. Verify connectivity: `curl http://localhost:15672`

**Docker Compose Snippet:**
```yaml
rabbitmq:
  image: rabbitmq:3.12-management
  ports:
    - "5672:5672"
    - "15672:15672"
  environment:
    RABBITMQ_DEFAULT_USER: guest
    RABBITMQ_DEFAULT_PASS: guest
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq
```

### 1.2 Domoticz Setup

**Deliverable:** Domoticz API accessible and tested

**Steps:**
1. Install/verify Domoticz running (typically port 8080)
2. Document API endpoint: `http://domoticz-host:8080/json.htm`
3. Create test devices (switches, sensors) if needed
4. Test API call:
   ```bash
   curl "http://localhost:8080/json.htm?type=devices&rid=0"
   ```
5. Document device IDs (idx) for later use

### 1.3 Directory Structure

```
automation-system/
├── dags/                          # Airflow DAGs
│   ├── __init__.py
│   ├── device_automation_dag.py
│   └── ui_test_dag.py
├── agents/
│   ├── device_agent/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── agent.py
│   └── ui_agent/
│       ├── Dockerfile
│       ├── package.json
│       ├── playwright.config.ts
│       └── tests/
│           └── example.spec.ts
├── ui_tests/                      # Standalone Playwright tests
│   ├── package.json
│   └── tests/
├── docker-compose.yml
├── Jenkinsfile
├── .gitignore
└── README.md
```

---

## Phase 2: Playwright Agent (UI Automation)

### 2.1 Project Initialization

**Deliverable:** Playwright agent Docker image ready

**Steps:**
1. Create `agents/ui_agent/` directory
2. Initialize Node.js project:
   ```bash
   cd agents/ui_agent
   npm init -y
   npm install --save-dev @playwright/test
   ```
3. Create `playwright.config.ts` with base configuration
4. Create example test in `tests/example.spec.ts`

### 2.2 Dockerfile for Playwright

**File:** `agents/ui_agent/Dockerfile`

```dockerfile
FROM mcr.microsoft.com/playwright:focal

WORKDIR /app

COPY package*.json ./
RUN npm ci && npx playwright install --with-deps

COPY . .

# Default command: run tests
CMD ["npx", "playwright", "test"]
```

### 2.3 Local Verification

```bash
cd agents/ui_agent
docker build -t playwright-agent:latest .
docker run --rm playwright-agent:latest
```

### 2.4 Test Example

**File:** `agents/ui_agent/tests/example.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('example test', async ({ page }) => {
  await page.goto('https://example.com');
  const title = await page.title();
  expect(title).toContain('Example');
});
```

---

## Phase 3: Device Agent (Domoticz Integration)

### 3.1 Python Environment

**File:** `agents/device_agent/requirements.txt`

```
requests==2.31.0
pika==1.3.2
python-dotenv==1.0.0
```

### 3.2 Device Agent Implementation

**File:** `agents/device_agent/agent.py`

**Core Responsibilities:**
- Subscribe to RabbitMQ for device commands
- Call Domoticz JSON API
- Publish device status updates
- Handle errors and retries

**Pseudo-code Structure:**
```python
import pika
import requests
import json
import os

DOMOTICZ_URL = os.getenv('DOMOTICZ_URL', 'http://localhost:8080')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

def toggle_device(idx, action):
    """Call Domoticz API to toggle device"""
    url = f"{DOMOTICZ_URL}/json.htm?type=command&param=switchlight&idx={idx}&switchcmd={action}"
    response = requests.get(url)
    return response.json()

def on_message(ch, method, properties, body):
    """Handle incoming RabbitMQ messages"""
    msg = json.loads(body)
    idx = msg.get('idx')
    action = msg.get('action')  # 'On' or 'Off'
    
    result = toggle_device(idx, action)
    
    # Publish status back
    publish_status(idx, result)

def publish_status(idx, status):
    """Publish device status to RabbitMQ"""
    # Implementation here

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='home', exchange_type='topic', durable=True)
    channel.queue_declare(queue='device_commands', durable=True)
    channel.queue_bind(exchange='home', queue='device_commands', routing_key='device.#.cmd')
    
    channel.basic_consume(queue='device_commands', on_message_callback=on_message, auto_ack=True)
    
    print('Device Agent listening...')
    channel.start_consuming()

if __name__ == '__main__':
    main()
```

### 3.3 Dockerfile for Device Agent

**File:** `agents/device_agent/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

CMD ["python", "agent.py"]
```

---

## Phase 4: Apache Airflow Orchestration

### 4.1 Airflow Setup (Docker Compose)

**Add to `docker-compose.yml`:**

```yaml
airflow-webserver:
  image: apache/airflow:2.7.0
  environment:
    AIRFLOW__CORE__DAGS_FOLDER: /opt/airflow/dags
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
  ports:
    - "8080:8080"
  volumes:
    - ./dags:/opt/airflow/dags
    - airflow_logs:/opt/airflow/logs
  command: webserver

airflow-scheduler:
  image: apache/airflow:2.7.0
  environment:
    AIRFLOW__CORE__DAGS_FOLDER: /opt/airflow/dags
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
  volumes:
    - ./dags:/opt/airflow/dags
    - airflow_logs:/opt/airflow/logs
  command: scheduler
  depends_on:
    - airflow-webserver
```

### 4.2 Example DAG: Device Automation

**File:** `dags/device_automation_dag.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pika
import json

default_args = {
    'owner': 'automation',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

def send_device_command(idx, action):
    """Send command to Device Agent via RabbitMQ"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    
    message = {'idx': idx, 'action': action}
    channel.basic_publish(
        exchange='home',
        routing_key=f'device.{idx}.cmd',
        body=json.dumps(message)
    )
    connection.close()

with DAG(
    'device_automation_dag',
    default_args=default_args,
    description='Automate Domoticz device control',
    schedule_interval='0 9 * * *',  # Daily at 9 AM
    start_date=datetime(2024, 1, 1),
) as dag:
    
    turn_on_task = PythonOperator(
        task_id='turn_on_device',
        python_callable=send_device_command,
        op_kwargs={'idx': 1, 'action': 'On'},
    )
    
    turn_off_task = PythonOperator(
        task_id='turn_off_device',
        python_callable=send_device_command,
        op_kwargs={'idx': 1, 'action': 'Off'},
    )
    
    turn_on_task >> turn_off_task
```

### 4.3 Example DAG: UI Tests

**File:** `dags/ui_test_dag.py`

```python
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'automation',
    'retries': 1,
}

with DAG(
    'ui_test_dag',
    default_args=default_args,
    schedule_interval='0 */6 * * *',  # Every 6 hours
    start_date=datetime(2024, 1, 1),
) as dag:
    
    run_playwright = DockerOperator(
        task_id='run_playwright_tests',
        image='playwright-agent:latest',
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
    )
```

---

## Phase 5: Jenkins CI/CD Pipeline

### 5.1 Jenkins Setup

**Required Plugins:**
- Docker Pipeline
- Git
- Pipeline
- Credentials Binding
- Email Extension

### 5.2 Jenkinsfile

**File:** `Jenkinsfile`

```groovy
pipeline {
    agent any
    
    environment {
        REGISTRY = 'docker.io'
        REGISTRY_CREDS = credentials('docker-registry-creds')
        AIRFLOW_HOST = 'http://airflow-webserver:8080'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Playwright Agent') {
            steps {
                script {
                    sh '''
                        cd agents/ui_agent
                        docker build -t ${REGISTRY}/playwright-agent:${BUILD_NUMBER} .
                    '''
                }
            }
        }
        
        stage('Build Device Agent') {
            steps {
                script {
                    sh '''
                        cd agents/device_agent
                        docker build -t ${REGISTRY}/device-agent:${BUILD_NUMBER} .
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    sh '''
                        docker run --rm ${REGISTRY}/playwright-agent:${BUILD_NUMBER}
                    '''
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                script {
                    sh '''
                        echo $REGISTRY_CREDS_PSW | docker login -u $REGISTRY_CREDS_USR --password-stdin ${REGISTRY}
                        docker push ${REGISTRY}/playwright-agent:${BUILD_NUMBER}
                        docker push ${REGISTRY}/device-agent:${BUILD_NUMBER}
                    '''
                }
            }
        }
        
        stage('Deploy DAGs to Airflow') {
            steps {
                script {
                    sh '''
                        cp dags/*.py /path/to/airflow/dags/
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext(
                subject: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

---

## Phase 6: Integration & Messaging Architecture

### 6.1 RabbitMQ Topic Structure

```
home/
├── device/
│   ├── {idx}/
│   │   ├── cmd          (commands to device)
│   │   └── status       (device status updates)
├── ui/
│   ├── {test_id}/
│   │   └── result       (test results)
└── system/
    ├── health           (heartbeats)
    └── events           (system events)
```

### 6.2 Message Format (JSON)

**Device Command:**
```json
{
  "correlation_id": "uuid-1234",
  "timestamp": "2024-01-15T10:30:00Z",
  "idx": 5,
  "action": "On",
  "source": "airflow-dag"
}
```

**Device Status:**
```json
{
  "correlation_id": "uuid-1234",
  "timestamp": "2024-01-15T10:30:02Z",
  "idx": 5,
  "status": "On",
  "level": 100,
  "source": "device-agent"
}
```

**Test Result:**
```json
{
  "correlation_id": "uuid-5678",
  "timestamp": "2024-01-15T10:35:00Z",
  "test_id": "ui_login_test",
  "passed": true,
  "duration_ms": 2500,
  "source": "playwright-agent"
}
```

### 6.3 Correlation ID Tracking

- Generate UUID for each workflow initiation
- Pass through all messages in the chain
- Log correlation ID in all services
- Use for end-to-end tracing

---

## Phase 7: Real-Time Event Handling

### 7.1 WebSocket Server (Optional)

**Purpose:** Live dashboard updates

**Technology:** Node.js + Socket.io

**Flow:**
```
RabbitMQ → Event Listener → WebSocket Server → Dashboard
```

### 7.2 Event Propagation Chain

```
Domoticz Device Change
  ↓
Device Agent (polls or webhook)
  ↓
Publish to RabbitMQ (home/device/{idx}/status)
  ↓
Airflow DAG (listens for events)
  ↓
Trigger UI tests or other actions
  ↓
Publish results back to RabbitMQ
  ↓
WebSocket → Dashboard
```

---

## Phase 8: Logging, Monitoring & Observability

### 8.1 Logging Strategy

**Components:**
- **Airflow:** Built-in task logs (stored in volumes)
- **Device Agent:** Python logging to stdout (captured by Docker)
- **Playwright Agent:** Test reports + screenshots on failure
- **RabbitMQ:** Management console logs

**Centralized Logging (Optional):**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki + Grafana

### 8.2 Monitoring

**Metrics to Track:**
- DAG execution time
- Task success/failure rates
- Device command latency
- Message queue depth
- Test pass/fail rates

**Tools:**
- Prometheus (metrics collection)
- Grafana (visualization)
- RabbitMQ Management Console (queue monitoring)

### 8.3 Alerts

**Trigger Conditions:**
- DAG failure
- Device command timeout
- Message queue backlog > threshold
- Test failure rate > threshold

**Channels:** Email, Slack, PagerDuty

---

## Phase 9: Security & Reliability

### 9.1 Authentication & Authorization

**Domoticz API:**
- Enable API key authentication
- Use HTTPS (reverse proxy with nginx/traefik)
- Restrict API access by IP

**Airflow:**
- Enable authentication (LDAP, OAuth, or local users)
- Use role-based access control (RBAC)

**Jenkins:**
- Enable authentication
- Use API tokens for automation
- Restrict job permissions

**RabbitMQ:**
- Change default credentials
- Create user per service
- Restrict queue/exchange permissions

### 9.2 Secrets Management

**Options:**
1. **Environment Variables** (dev only)
2. **Jenkins Credentials** (for CI/CD)
3. **Airflow Variables/Connections** (for DAGs)
4. **HashiCorp Vault** (production)

**Example (Airflow):**
```python
from airflow.models import Variable

domoticz_url = Variable.get("domoticz_url")
rabbitmq_host = Variable.get("rabbitmq_host")
```

### 9.3 Retry & Idempotency

**DAG Task Retry:**
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}
```

**Idempotent Device Commands:**
- Use device state checks before action
- Implement request deduplication (correlation ID)
- Log all actions for audit trail

### 9.4 Error Handling

**Device Agent:**
```python
try:
    result = toggle_device(idx, action)
except requests.exceptions.Timeout:
    # Retry logic
except requests.exceptions.ConnectionError:
    # Fallback or alert
```

**Playwright Tests:**
```typescript
test.setTimeout(30000);
test.retries = 2;
```

---

## Phase 10: Testing & Deployment

### 10.1 Pre-Deployment Checklist

- [ ] All Docker images build successfully
- [ ] docker-compose up -d runs without errors
- [ ] RabbitMQ management console accessible
- [ ] Airflow webserver accessible
- [ ] Jenkins pipeline runs successfully
- [ ] Device Agent connects to RabbitMQ
- [ ] Device Agent can call Domoticz API
- [ ] Playwright tests run in Docker
- [ ] Message passing verified end-to-end

### 10.2 Deployment Steps

**1. Prepare Infrastructure:**
```bash
git clone <repo>
cd automation-system
docker-compose up -d
```

**2. Verify Services:**
```bash
docker-compose ps
curl http://localhost:15672  # RabbitMQ
curl http://localhost:8080   # Airflow
```

**3. Deploy DAGs:**
```bash
cp dags/*.py /path/to/airflow/dags/
```

**4. Trigger Test DAG:**
- Access Airflow UI
- Enable `device_automation_dag`
- Trigger manually
- Monitor execution

**5. Verify Message Flow:**
```bash
# Terminal 1: Listen to RabbitMQ
docker exec rabbitmq rabbitmqctl list_queues

# Terminal 2: Publish test message
# (via Device Agent or manual script)
```

### 10.3 Optimization & Tuning

**Performance:**
- Increase Airflow parallelism for concurrent DAGs
- Configure RabbitMQ prefetch limits
- Optimize Playwright timeouts

**Reliability:**
- Implement circuit breakers for Domoticz API
- Add health checks to all services
- Configure auto-restart policies

**Observability:**
- Enable detailed logging
- Set up centralized log aggregation
- Create dashboards for key metrics

---

## Phase 11: Production Hardening

### 11.1 Kubernetes Deployment (Optional)

**Benefits:**
- Auto-scaling
- Self-healing
- Rolling updates
- Better resource management

**Components:**
- Airflow Helm Chart
- RabbitMQ StatefulSet
- Device Agent Deployment
- Playwright Agent Job

### 11.2 Backup & Disaster Recovery

**Backup Strategy:**
- Airflow metadata database
- RabbitMQ queue persistence
- DAG definitions (Git)
- Configuration files

**Recovery Plan:**
- Document restore procedures
- Test recovery regularly
- Maintain off-site backups

### 11.3 Performance Tuning

**Airflow:**
- Tune executor parallelism
- Optimize DAG parsing
- Use connection pooling

**RabbitMQ:**
- Configure memory limits
- Tune queue durability
- Monitor queue depth

---

## Summary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTOMATION SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Domoticz    │◄────────┤ Device Agent │                 │
│  │  Devices     │         │  (Python)    │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                  │                          │
│                           ┌──────▼────────┐                │
│                           │   RabbitMQ    │                │
│                           │   (Broker)    │                │
│                           └──────┬────────┘                │
│                                  │                          │
│         ┌────────────────────────┼────────────────────┐    │
│         │                        │                    │    │
│    ┌────▼────────┐      ┌────────▼──────┐    ┌──────▼──┐ │
│    │  Airflow    │      │  UI Agent     │    │Dashboard│ │
│    │  (DAGs)     │      │ (Playwright)  │    │(WS)     │ │
│    └────┬────────┘      └───────────────┘    └─────────┘ │
│         │                                                  │
│    ┌────▼────────────────────────────────┐               │
│    │      Jenkins CI/CD Pipeline         │               │
│    │  (Build, Test, Deploy, Monitor)     │               │
│    └─────────────────────────────────────┘               │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start Commands

```bash
# Clone and setup
git clone <repo>
cd automation-system

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f rabbitmq
docker-compose logs -f airflow-webserver

# Access UIs
# RabbitMQ: http://localhost:15672 (guest/guest)
# Airflow: http://localhost:8080 (airflow/airflow)

# Trigger DAG
curl -X POST http://localhost:8080/api/v1/dags/device_automation_dag/dagRuns

# Stop all services
docker-compose down
```

---

## Next Steps

1. **Start Phase 0:** Validate all prerequisites
2. **Start Phase 1:** Set up RabbitMQ and Domoticz
3. **Parallel Phases 2-3:** Build Playwright and Device agents
4. **Phase 4:** Deploy Airflow with example DAGs
5. **Phase 5:** Configure Jenkins pipeline
6. **Phase 6:** Test end-to-end message flow
7. **Phases 7-11:** Add monitoring, security, and optimization

---

**Last Updated:** 2024-01-15  
**Status:** Ready for Implementation
