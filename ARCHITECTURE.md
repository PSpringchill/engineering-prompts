# System Architecture & Design

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT AUTOMATION SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         EXTERNAL SYSTEMS                             │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐  │  │
│  │  │  Domoticz       │    │  Web Applications│    │  Monitoring  │  │  │
│  │  │  (Devices)      │    │  (UI Tests)      │    │  Systems     │  │  │
│  │  └────────┬────────┘    └────────┬─────────┘    └──────┬───────┘  │  │
│  │           │                      │                     │           │  │
│  └───────────┼──────────────────────┼─────────────────────┼───────────┘  │
│              │                      │                     │               │
│  ┌───────────▼──────────────────────▼─────────────────────▼───────────┐  │
│  │                    CORE MESSAGING LAYER                            │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │              RabbitMQ Message Broker                     │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐ │    │  │
│  │  │  │ Exchanges:                                         │ │    │  │
│  │  │  │  • home (topic) - device commands                 │ │    │  │
│  │  │  │  • home_status (topic) - device status updates    │ │    │  │
│  │  │  │  • ui_results (topic) - test results             │ │    │  │
│  │  │  │  • system (topic) - system events                │ │    │  │
│  │  │  └────────────────────────────────────────────────────┘ │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐ │    │  │
│  │  │  │ Queues:                                            │ │    │  │
│  │  │  │  • device_commands (durable)                       │ │    │  │
│  │  │  │  • ui_test_results (durable)                       │ │    │  │
│  │  │  │  • system_events (durable)                         │ │    │  │
│  │  │  └────────────────────────────────────────────────────┘ │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                      AGENT LAYER                                   │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐              │  │
│  │  │  Device Agent        │  │  UI Agent            │              │  │
│  │  │  (Python)            │  │  (Node.js/Playwright)│              │  │
│  │  │                      │  │                      │              │  │
│  │  │ ┌──────────────────┐ │  │ ┌──────────────────┐ │              │  │
│  │  │ │ RabbitMQ Client  │ │  │ │ RabbitMQ Client  │ │              │  │
│  │  │ │ (pika)           │ │  │ │ (amqplib)        │ │              │  │
│  │  │ └────────┬─────────┘ │  │ └────────┬─────────┘ │              │  │
│  │  │          │            │  │          │           │              │  │
│  │  │ ┌────────▼─────────┐ │  │ ┌────────▼─────────┐ │              │  │
│  │  │ │ Domoticz API     │ │  │ │ Playwright Tests │ │              │  │
│  │  │ │ Integration      │ │  │ │ Execution       │ │              │  │
│  │  │ └──────────────────┘ │  │ └──────────────────┘ │              │  │
│  │  │                      │  │                      │              │  │
│  │  └──────────────────────┘  └──────────────────────┘              │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                   ORCHESTRATION LAYER                              │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │         Apache Airflow (DAG Orchestration)              │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐ │    │  │
│  │  │  │ DAGs:                                              │ │    │  │
│  │  │  │  • device_automation_dag - device control flow    │ │    │  │
│  │  │  │  • ui_test_dag - UI test execution               │ │    │  │
│  │  │  │  • integration_dag - end-to-end workflows        │ │    │  │
│  │  │  └────────────────────────────────────────────────────┘ │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐ │    │  │
│  │  │  │ Components:                                        │ │    │  │
│  │  │  │  • Webserver (UI, REST API)                       │ │    │  │
│  │  │  │  • Scheduler (DAG execution)                      │ │    │  │
│  │  │  │  • Executor (LocalExecutor/CeleryExecutor)        │ │    │  │
│  │  │  │  • Metadata DB (SQLite/PostgreSQL)                │ │    │  │
│  │  │  └────────────────────────────────────────────────────┘ │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    CI/CD LAYER                                     │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │              Jenkins Pipeline                           │    │  │
│  │  │  ┌────────────────────────────────────────────────────┐ │    │  │
│  │  │  │ Stages:                                            │ │    │  │
│  │  │  │  1. Checkout (Git)                                │ │    │  │
│  │  │  │  2. Build (Docker images)                         │ │    │  │
│  │  │  │  3. Test (Unit & Integration)                     │ │    │  │
│  │  │  │  4. Push (Container Registry)                     │ │    │  │
│  │  │  │  5. Deploy (Airflow DAGs)                         │ │    │  │
│  │  │  └────────────────────────────────────────────────────┘ │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                   OBSERVABILITY LAYER                              │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │ Logging      │  │ Monitoring   │  │ Alerting     │            │  │
│  │  │ (ELK/Loki)   │  │ (Prometheus) │  │ (PagerDuty)  │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Message Flow Diagram

### Device Control Flow

```
User/Airflow DAG
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ Publish Device Command to RabbitMQ                          │
│ Topic: home/device/{idx}/cmd                                │
│ Message: {idx, action, correlation_id, timestamp}           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   RabbitMQ Message Broker   │
         │   Queue: device_commands    │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Device Agent (Consumer)    │
         │   - Receive message          │
         │   - Parse command            │
         │   - Call Domoticz API        │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Domoticz API Call          │
         │   /json.htm?type=command...  │
         │   - Toggle device            │
         │   - Get status               │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Device Agent               │
         │   - Publish status update    │
         │   - Log action               │
         └──────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Publish Device Status to RabbitMQ                           │
│ Topic: home_status/device/{idx}/status                      │
│ Message: {idx, status, level, correlation_id, timestamp}    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   RabbitMQ Message Broker   │
         │   Topic: home_status        │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Airflow / Dashboard        │
         │   - Receive status           │
         │   - Update state             │
         │   - Trigger next task        │
         └──────────────────────────────┘
```

### UI Test Flow

```
Airflow DAG (ui_test_dag)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ Trigger Playwright Tests via DockerOperator                 │
│ - Pull ui-agent Docker image                                │
│ - Mount test directory                                      │
│ - Set environment variables                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │   Docker Container           │
         │   (ui-agent)                 │
         │   - npm test                 │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Playwright Test Execution  │
         │   - Launch browser           │
         │   - Run test scenarios       │
         │   - Capture screenshots      │
         │   - Generate reports         │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Test Results               │
         │   - HTML report              │
         │   - JSON results             │
         │   - JUnit XML                │
         │   - Screenshots/Videos       │
         └──────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Publish Test Results to RabbitMQ (Optional)                 │
│ Topic: ui_results/test/{test_id}/result                     │
│ Message: {test_id, passed, duration, correlation_id}        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   Airflow / Dashboard       │
         │   - Receive results         │
         │   - Update metrics          │
         │   - Trigger alerts if fail  │
         └─────────────────────────────┘
```

---

## Data Model

### Device Command Message

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "source": "airflow-dag",
  "idx": 5,
  "action": "On",
  "metadata": {
    "user": "automation",
    "reason": "scheduled_automation",
    "priority": "normal"
  }
}
```

### Device Status Message

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:02.000Z",
  "source": "device-agent",
  "agent_id": "agent-001",
  "idx": 5,
  "result": {
    "success": true,
    "status": "On",
    "level": 100,
    "name": "Living Room Light",
    "type": "Light"
  }
}
```

### Test Result Message

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:35:00.000Z",
  "source": "ui-agent",
  "test_id": "ui_login_test",
  "result": {
    "passed": true,
    "duration_ms": 2500,
    "browser": "chromium",
    "screenshots": [
      "/test-results/screenshots/login-step-1.png"
    ]
  }
}
```

---

## Component Interaction Matrix

| Component | RabbitMQ | Domoticz | Airflow | Jenkins | Docker |
|-----------|----------|----------|---------|---------|--------|
| Device Agent | Producer/Consumer | Consumer | - | - | Container |
| UI Agent | Producer | - | - | - | Container |
| Airflow | Producer | - | Orchestrator | - | Container |
| Jenkins | - | - | - | CI/CD | Orchestrator |
| Dashboard | Consumer | - | - | - | Container |

---

## Deployment Topology

### Development (Single Machine)

```
┌─────────────────────────────────────┐
│   Docker Compose (Single Host)      │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ RabbitMQ                    │   │
│  │ Airflow (Web + Scheduler)   │   │
│  │ Device Agent                │   │
│  │ UI Agent (on demand)        │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### Production (Kubernetes)

```
┌──────────────────────────────────────────────────────────┐
│         Kubernetes Cluster                               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Namespace: automation                              │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ RabbitMQ StatefulSet (3 replicas)            │ │ │
│  │  │ - Persistent storage                         │ │ │
│  │  │ - Service: rabbitmq.automation.svc.cluster   │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ Airflow Deployment (Helm Chart)              │ │ │
│  │  │ - Web Server (1 replica)                     │ │ │
│  │  │ - Scheduler (1 replica)                      │ │ │
│  │  │ - PostgreSQL (1 replica)                     │ │ │
│  │  │ - Ingress: airflow.example.com               │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ Device Agent Deployment (2-5 replicas)       │ │ │
│  │  │ - Auto-scaling based on queue depth          │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ UI Agent Job (on-demand)                     │ │ │
│  │  │ - Triggered by Airflow                       │ │ │
│  │  │ - Runs to completion                         │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ Monitoring Stack (Optional)                  │ │ │
│  │  │ - Prometheus                                 │ │ │
│  │  │ - Grafana                                    │ │ │
│  │  │ - Loki (log aggregation)                     │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Messaging** | RabbitMQ 3.12 | Message broker for inter-agent communication |
| **Device Control** | Domoticz JSON API | Home automation device management |
| **Device Agent** | Python 3.11 | Domoticz integration and device control |
| **UI Testing** | Playwright | Cross-browser UI automation |
| **UI Agent** | Node.js 18+ | Playwright test execution |
| **Orchestration** | Apache Airflow 2.7 | DAG scheduling and workflow management |
| **CI/CD** | Jenkins | Build, test, and deployment automation |
| **Containerization** | Docker 20.10+ | Container runtime |
| **Orchestration** | Docker Compose / Kubernetes | Container orchestration |
| **Logging** | ELK / Loki | Centralized log aggregation |
| **Monitoring** | Prometheus / Grafana | Metrics and visualization |
| **Database** | SQLite / PostgreSQL | Airflow metadata storage |

---

## Scalability Considerations

### Horizontal Scaling
- **Device Agent:** Multiple instances consuming from same RabbitMQ queue
- **Playwright Tests:** Parallel execution via Airflow parallelism
- **Airflow Workers:** Scale with CeleryExecutor or KubernetesExecutor

### Vertical Scaling
- Increase RabbitMQ memory and connection limits
- Increase Airflow scheduler resources
- Increase Domoticz API server capacity

### Performance Optimization
- RabbitMQ prefetch tuning
- Airflow DAG parsing optimization
- Connection pooling for Domoticz API
- Playwright test parallelization

---

## Disaster Recovery

### RTO/RPO Targets
- **RTO (Recovery Time Objective):** < 1 hour
- **RPO (Recovery Point Objective):** < 5 minutes

### Backup Strategy
- Daily snapshots of Airflow metadata DB
- RabbitMQ queue persistence to disk
- Git repository for DAG definitions
- Configuration file backups

### Failover Mechanisms
- RabbitMQ clustering for HA
- Airflow scheduler redundancy
- Device Agent auto-restart on failure
- Health checks on all services

---

**Last Updated:** 2024-01-15
