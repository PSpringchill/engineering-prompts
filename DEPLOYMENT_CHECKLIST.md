# Deployment Checklist

## Phase 0: Prerequisites ✓

### Environment
- [ ] Linux server/VM or Kubernetes cluster available
- [ ] Docker installed (version >= 20.10)
- [ ] Docker Compose installed (version >= 1.29)
- [ ] Git installed and configured
- [ ] Node.js >= 16 and npm installed
- [ ] Python >= 3.9 installed
- [ ] Sufficient disk space (min 10GB)
- [ ] Network connectivity verified

### External Services
- [ ] Jenkins server accessible (note URL and credentials)
- [ ] Domoticz server accessible (note URL and API endpoint)
- [ ] Container registry access configured (DockerHub/GitHub/private)
- [ ] SMTP server available (for alerts, optional)

### Accounts & Credentials
- [ ] Docker Hub account created (if using public registry)
- [ ] Jenkins admin credentials saved
- [ ] Domoticz API key/credentials documented
- [ ] SSH keys configured for Git access

---

## Phase 1: Core Infrastructure ✓

### RabbitMQ Setup
- [ ] RabbitMQ image pulled: `docker pull rabbitmq:3.12-management`
- [ ] Management plugin enabled (port 15672)
- [ ] Default credentials changed (production only)
- [ ] Persistence volume created
- [ ] Health check configured
- [ ] Management console accessible at http://localhost:15672

### Domoticz Integration
- [ ] Domoticz running and accessible
- [ ] JSON API endpoint verified: `curl http://domoticz:8080/json.htm?type=devices`
- [ ] Test devices created (at least 1 switch)
- [ ] Device IDs documented
- [ ] API response format verified
- [ ] TLS/HTTPS configured (production)

### Directory Structure
- [ ] `automation-system/` root directory created
- [ ] `dags/` directory created
- [ ] `agents/device_agent/` directory created
- [ ] `agents/ui_agent/` directory created
- [ ] `ui_tests/` directory created
- [ ] `.gitignore` file created
- [ ] `README.md` created

---

## Phase 2: Playwright Agent ✓

### Project Setup
- [ ] `agents/ui_agent/` initialized with `npm init -y`
- [ ] `package.json` configured with Playwright dependency
- [ ] `@playwright/test` installed
- [ ] `playwright.config.ts` created with base configuration
- [ ] `tests/` directory created

### Test Implementation
- [ ] Example test created in `tests/example.spec.ts`
- [ ] Test runs locally: `npm test`
- [ ] Test reports generated (HTML, JSON, JUnit)
- [ ] Screenshots captured on failure
- [ ] Video recording configured

### Docker Setup
- [ ] `Dockerfile` created for Playwright agent
- [ ] Base image: `mcr.microsoft.com/playwright:focal`
- [ ] Dependencies installed in image
- [ ] Image builds successfully: `docker build -t playwright-agent .`
- [ ] Image runs successfully: `docker run --rm playwright-agent`
- [ ] Test results mounted to host volume

---

## Phase 3: Device Agent ✓

### Python Environment
- [ ] `agents/device_agent/` directory created
- [ ] `requirements.txt` created with dependencies:
  - [ ] requests
  - [ ] pika
  - [ ] python-dotenv
  - [ ] structlog
  - [ ] tenacity
- [ ] Virtual environment created (optional): `python -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`

### Agent Implementation
- [ ] `agent.py` created with core functionality:
  - [ ] RabbitMQ connection with retry logic
  - [ ] Exchange/queue declaration
  - [ ] Message consumer callback
  - [ ] Domoticz API integration
  - [ ] Device toggle functionality
  - [ ] Status publishing
  - [ ] Error handling and logging
- [ ] `.env` file created with configuration
- [ ] Agent runs locally: `python agent.py`
- [ ] RabbitMQ connectivity verified
- [ ] Domoticz API calls tested

### Docker Setup
- [ ] `Dockerfile` created for Device agent
- [ ] Base image: `python:3.11-slim`
- [ ] Dependencies installed in image
- [ ] Image builds successfully: `docker build -t device-agent .`
- [ ] Image runs successfully: `docker run --rm device-agent`
- [ ] Health check configured
- [ ] Logs mounted to host volume

---

## Phase 4: Apache Airflow ✓

### Airflow Setup
- [ ] Airflow image pulled: `apache/airflow:2.7.0-python3.11`
- [ ] Webserver service configured in docker-compose
- [ ] Scheduler service configured in docker-compose
- [ ] Database initialized
- [ ] Webserver accessible at http://localhost:8080
- [ ] Default credentials set (airflow/airflow)

### DAG Development
- [ ] `dags/` directory created
- [ ] `dags/__init__.py` created
- [ ] `dags/device_automation_dag.py` created:
  - [ ] PythonOperator for device commands
  - [ ] RabbitMQ integration
  - [ ] Task dependencies defined
  - [ ] Schedule interval configured
  - [ ] Error handling implemented
- [ ] `dags/ui_test_dag.py` created:
  - [ ] DockerOperator for Playwright tests
  - [ ] Image reference configured
  - [ ] Network mode set correctly
  - [ ] Volume mounts configured

### DAG Testing
- [ ] DAG syntax verified: `python -m py_compile dags/*.py`
- [ ] DAGs appear in Airflow UI
- [ ] Manual DAG trigger successful
- [ ] Task execution monitored
- [ ] Logs accessible in Airflow UI

---

## Phase 5: Jenkins CI/CD ✓

### Jenkins Setup
- [ ] Jenkins server installed/accessible
- [ ] Required plugins installed:
  - [ ] Docker Pipeline
  - [ ] Git
  - [ ] Pipeline
  - [ ] Credentials Binding
  - [ ] Email Extension
- [ ] Jenkins user created with appropriate permissions
- [ ] Docker socket accessible to Jenkins

### Jenkinsfile
- [ ] `Jenkinsfile` created in repository root
- [ ] Stages defined:
  - [ ] Checkout
  - [ ] Build Playwright Agent
  - [ ] Build Device Agent
  - [ ] Run Tests
  - [ ] Push to Registry
  - [ ] Deploy DAGs
- [ ] Environment variables configured
- [ ] Credentials configured:
  - [ ] Docker registry credentials
  - [ ] Airflow API credentials
  - [ ] Email notifications
- [ ] Post-build actions configured

### Pipeline Testing
- [ ] Pipeline created in Jenkins
- [ ] Repository connected to Jenkins
- [ ] Webhook configured (optional)
- [ ] Manual pipeline trigger successful
- [ ] Build artifacts archived
- [ ] Test reports published
- [ ] Docker images pushed to registry

---

## Phase 6: Integration & Messaging ✓

### RabbitMQ Topics
- [ ] Exchange `home` created (topic type)
- [ ] Exchange `home_status` created (topic type)
- [ ] Queue `device_commands` created
- [ ] Queue bindings configured:
  - [ ] `device.#.cmd` → `device_commands`
  - [ ] `device.#.status` → status listeners
- [ ] Message persistence enabled
- [ ] Dead-letter exchange configured (optional)

### Message Format
- [ ] Device command schema defined and documented
- [ ] Device status schema defined and documented
- [ ] Test result schema defined and documented
- [ ] Correlation ID tracking implemented
- [ ] Timestamp format standardized (ISO 8601)

### End-to-End Testing
- [ ] Send device command via RabbitMQ
- [ ] Device Agent receives and processes
- [ ] Device Agent calls Domoticz API
- [ ] Device Agent publishes status
- [ ] Status message received and logged
- [ ] Correlation ID tracked through chain

---

## Phase 7: Real-Time Event Handling ✓

### Event Propagation
- [ ] Domoticz event listener configured (webhook or polling)
- [ ] Events published to RabbitMQ
- [ ] Airflow DAG listens for events
- [ ] DAG triggers on event receipt
- [ ] Event correlation tracked
- [ ] Event logging implemented

### WebSocket Server (Optional)
- [ ] WebSocket server code written (Node.js/Socket.io)
- [ ] RabbitMQ listener integrated
- [ ] Dashboard frontend created
- [ ] Real-time updates flowing to dashboard
- [ ] Reconnection logic implemented
- [ ] Error handling for dropped connections

---

## Phase 8: Logging & Monitoring ✓

### Logging Strategy
- [ ] Airflow logs configured and accessible
- [ ] Device Agent logs to stdout/file
- [ ] Playwright test reports generated
- [ ] RabbitMQ logs accessible
- [ ] Centralized logging configured (optional):
  - [ ] ELK Stack or Loki deployed
  - [ ] Log shipper configured
  - [ ] Dashboards created

### Monitoring
- [ ] Prometheus installed (optional)
- [ ] Metrics exported from services
- [ ] Grafana dashboards created (optional)
- [ ] Key metrics identified:
  - [ ] DAG execution time
  - [ ] Task success/failure rates
  - [ ] Device command latency
  - [ ] Message queue depth
  - [ ] Test pass/fail rates

### Alerts
- [ ] Alert rules defined
- [ ] Alert channels configured:
  - [ ] Email
  - [ ] Slack (optional)
  - [ ] PagerDuty (optional)
- [ ] Alert thresholds set
- [ ] Alert testing completed

---

## Phase 9: Security & Reliability ✓

### Authentication & Authorization
- [ ] Domoticz API authentication enabled
- [ ] Domoticz API TLS/HTTPS configured
- [ ] Airflow authentication enabled (LDAP/OAuth/local)
- [ ] Airflow RBAC configured
- [ ] Jenkins authentication enabled
- [ ] Jenkins API token created
- [ ] RabbitMQ default credentials changed
- [ ] RabbitMQ user per service created
- [ ] RabbitMQ permissions restricted

### Secrets Management
- [ ] Environment variables strategy defined
- [ ] Jenkins Credentials configured
- [ ] Airflow Variables/Connections configured
- [ ] Vault integration (optional)
- [ ] Secrets rotation policy defined
- [ ] Secrets not committed to Git

### Retry & Idempotency
- [ ] DAG task retries configured
- [ ] Retry delays set appropriately
- [ ] Device commands idempotent
- [ ] Request deduplication implemented
- [ ] Audit trail logging enabled

### Error Handling
- [ ] Device Agent error handling implemented
- [ ] Playwright test error handling
- [ ] Airflow task error handling
- [ ] Timeout configurations set
- [ ] Fallback mechanisms defined
- [ ] Circuit breaker pattern (optional)

---

## Phase 10: Testing & Deployment ✓

### Pre-Deployment Validation
- [ ] All Docker images build successfully
- [ ] `docker-compose up -d` runs without errors
- [ ] All services reach healthy state
- [ ] RabbitMQ management console accessible
- [ ] Airflow webserver accessible
- [ ] Jenkins pipeline runs successfully
- [ ] Device Agent connects to RabbitMQ
- [ ] Device Agent can call Domoticz API
- [ ] Playwright tests run in Docker
- [ ] Message passing verified end-to-end

### Deployment Steps
- [ ] Repository cloned to deployment server
- [ ] Environment variables configured
- [ ] Docker images built or pulled
- [ ] `docker-compose up -d` executed
- [ ] Service health verified
- [ ] DAGs deployed to Airflow
- [ ] Jenkins pipeline configured
- [ ] Monitoring dashboards accessible

### Post-Deployment Testing
- [ ] Manual DAG trigger successful
- [ ] Device command flow tested
- [ ] Playwright tests executed
- [ ] Message queue monitored
- [ ] Logs reviewed for errors
- [ ] Performance baseline established
- [ ] Backup procedures tested

---

## Phase 11: Production Hardening ✓

### Kubernetes Deployment (Optional)
- [ ] Kubernetes cluster available
- [ ] Airflow Helm Chart deployed
- [ ] RabbitMQ StatefulSet configured
- [ ] Device Agent Deployment created
- [ ] Playwright Agent Job configured
- [ ] Ingress configured
- [ ] PersistentVolumes configured
- [ ] Resource limits set

### Backup & Disaster Recovery
- [ ] Airflow metadata database backup strategy
- [ ] RabbitMQ queue persistence verified
- [ ] DAG definitions backed up (Git)
- [ ] Configuration files backed up
- [ ] Off-site backup location configured
- [ ] Recovery procedures documented
- [ ] Recovery tested

### Performance Tuning
- [ ] Airflow parallelism tuned
- [ ] RabbitMQ memory limits configured
- [ ] Connection pooling implemented
- [ ] Database query optimization
- [ ] Load testing completed
- [ ] Bottlenecks identified and addressed
- [ ] Performance metrics baseline established

---

## Final Verification

### System Health
- [ ] All services running and healthy
- [ ] No error messages in logs
- [ ] Performance metrics within acceptable range
- [ ] Backup procedures working
- [ ] Monitoring and alerting active
- [ ] Documentation complete and accurate

### Documentation
- [ ] README.md comprehensive
- [ ] Architecture diagram created
- [ ] API documentation complete
- [ ] Runbook for common operations created
- [ ] Troubleshooting guide created
- [ ] Disaster recovery procedures documented

### Team Readiness
- [ ] Team trained on system
- [ ] On-call procedures defined
- [ ] Escalation procedures defined
- [ ] Communication channels established
- [ ] Knowledge transfer completed

---

## Sign-Off

- [ ] Project Manager: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______
- [ ] QA Lead: _________________ Date: _______
- [ ] Security Lead: _________________ Date: _______

---

**Status:** Ready for Production Deployment
**Last Updated:** 2024-01-15
