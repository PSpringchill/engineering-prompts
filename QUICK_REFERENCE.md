# Quick Reference Guide

## 🚀 30-Second Overview

**What:** Multi-agent automation system (Playwright + Domoticz + Airflow + Jenkins)  
**Why:** Automate device control, UI testing, and workflows at scale  
**How:** Docker containers + RabbitMQ messaging + Airflow orchestration  
**Time:** 30 min setup (dev) → 4-5 weeks (production)  

---

## 📂 File Structure

```
automation-system/
├── dags/                          # Airflow DAGs
│   ├── __init__.py
│   ├── device_automation_dag.py
│   └── ui_test_dag.py
├── agents/
│   ├── device_agent/              # Python: Domoticz control
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── agent.py
│   │   ├── .env
│   │   └── logs/
│   └── ui_agent/                  # Node.js: Playwright tests
│       ├── Dockerfile
│       ├── package.json
│       ├── playwright.config.ts
│       ├── tests/
│       │   └── example.spec.ts
│       ├── test-results/
│       └── screenshots/
├── docker-compose.yml             # Service definitions
├── Jenkinsfile                    # CI/CD pipeline
├── .gitignore
└── README.md
```

---

## 🔧 Essential Commands

### Start/Stop Services
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose restart <service>  # Restart specific service
docker-compose logs -f <service>  # View logs
docker-compose ps                 # Check status
```

### Access UIs
```
RabbitMQ:  http://localhost:15672  (guest/guest)
Airflow:   http://localhost:8080   (airflow/airflow)
Domoticz:  http://localhost:8081   (if running)
```

### Test Messaging
```bash
# Send device command
python3 << 'EOF'
import pika, json
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
ch = conn.channel()
ch.exchange_declare(exchange='home', exchange_type='topic', durable=True)
msg = {'idx': 1, 'action': 'On', 'correlation_id': 'test-123'}
ch.basic_publish(exchange='home', routing_key='device.1.cmd', body=json.dumps(msg))
print("✓ Sent")
conn.close()
EOF
```

### Trigger DAG
```bash
curl -X POST http://localhost:8080/api/v1/dags/device_automation_dag/dagRuns \
  -H "Content-Type: application/json" -d '{"conf": {}}'
```

### Run Playwright Tests
```bash
docker-compose run --rm ui-agent npm test
```

---

## 📊 Service Ports

| Service | Port | Type | URL |
|---------|------|------|-----|
| RabbitMQ AMQP | 5672 | Internal | amqp://localhost:5672 |
| RabbitMQ UI | 15672 | Web | http://localhost:15672 |
| Airflow | 8080 | Web | http://localhost:8080 |
| Domoticz | 8081 | Web | http://localhost:8081 |

---

## 🔌 RabbitMQ Topics

```
home/
├── device/{idx}/cmd          → Device commands (to Device Agent)
├── device/{idx}/status       → Device status (from Device Agent)
├── ui/{test_id}/result       → Test results (from UI Agent)
└── system/
    ├── health                → Heartbeats
    └── events                → System events
```

---

## 📝 Message Formats

### Device Command
```json
{
  "correlation_id": "uuid-1234",
  "timestamp": "2024-01-15T10:30:00Z",
  "idx": 5,
  "action": "On",
  "source": "airflow-dag"
}
```

### Device Status
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

---

## 🐛 Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Connection refused" | `docker-compose restart rabbitmq` |
| DAG not visible | `docker-compose exec airflow-webserver airflow dags list` |
| Device not responding | `curl http://localhost:8081/json.htm?type=devices` |
| Tests timeout | Increase timeout in `playwright.config.ts` |
| No space left | `docker system prune -a` |
| Port in use | Change port in `docker-compose.yml` |

---

## 🔐 Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| RabbitMQ | guest | guest |
| Airflow | airflow | airflow |
| Domoticz | (none) | (none) |

**⚠️ Change in production!**

---

## 📋 Pre-Deployment Checklist

- [ ] All Docker images build successfully
- [ ] `docker-compose up -d` runs without errors
- [ ] RabbitMQ management console accessible
- [ ] Airflow webserver accessible
- [ ] Device Agent connects to RabbitMQ
- [ ] Device Agent can call Domoticz API
- [ ] Playwright tests run in Docker
- [ ] Message passing verified end-to-end
- [ ] Jenkins pipeline configured
- [ ] Monitoring/logging setup

---

## 🔄 Common Workflows

### Add New Device
```bash
# 1. Get device ID from Domoticz
curl http://localhost:8081/json.htm?type=devices | grep -i "device_name"

# 2. Update DAG with device ID
# Edit dags/device_automation_dag.py

# 3. Trigger DAG
curl -X POST http://localhost:8080/api/v1/dags/device_automation_dag/dagRuns \
  -H "Content-Type: application/json" -d '{"conf": {}}'
```

### Add New Test
```bash
# 1. Create test file
cat > agents/ui_agent/tests/new_test.spec.ts << 'EOF'
import { test, expect } from '@playwright/test';
test('my test', async ({ page }) => {
  // test code
});
EOF

# 2. Run tests
docker-compose run --rm ui-agent npm test

# 3. View results
open agents/ui_agent/test-results/html/index.html
```

### Deploy to Production
```bash
# 1. Update .env.production
# 2. Build images
docker-compose build

# 3. Push to registry
docker push myregistry/device-agent:latest
docker push myregistry/ui-agent:latest

# 4. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
docker-compose ps
docker-compose logs
```

---

## 📚 Documentation Map

```
START HERE
    ↓
QUICK_START.md (30 min setup)
    ↓
DOCUMENTATION_INDEX.md (find what you need)
    ↓
Choose your path:
├─ IMPLEMENTATION_PLAN.md (understand phases)
├─ TECHNICAL_SPECS.md (code templates)
├─ ARCHITECTURE.md (system design)
├─ DEPLOYMENT_CHECKLIST.md (verify progress)
└─ TROUBLESHOOTING.md (fix issues)
```

---

## ⚡ Performance Tuning

### RabbitMQ
```bash
# Increase prefetch for higher throughput
# In agent.py:
channel.basic_qos(prefetch_count=10)

# Set memory limit
docker-compose exec rabbitmq rabbitmqctl set_vm_memory_high_watermark 0.6
```

### Airflow
```bash
# Increase parallelism in docker-compose.yml
AIRFLOW__CORE__PARALLELISM: 32
AIRFLOW__CORE__DAG_CONCURRENCY: 16
```

### Playwright
```typescript
// In playwright.config.ts
workers: 4,
fullyParallel: true,
```

---

## 🔍 Debugging Commands

```bash
# Check service health
docker-compose exec rabbitmq rabbitmq-diagnostics ping
docker-compose exec airflow-webserver curl http://localhost:8080/health

# View queue status
docker-compose exec rabbitmq rabbitmqctl list_queues name messages consumers

# Check logs for errors
docker-compose logs rabbitmq | grep -i error
docker-compose logs device-agent | grep -i error
docker-compose logs airflow-scheduler | grep -i error

# Test connectivity
docker-compose exec device-agent ping rabbitmq
docker-compose exec device-agent curl http://domoticz:8080/json.htm?type=devices

# Monitor resource usage
docker stats
```

---

## 📈 Key Metrics

| Metric | Target | How to Check |
|--------|--------|-------------|
| Message latency | < 500ms | Correlation ID timestamps |
| DAG execution | < 5 min | Airflow UI |
| Test execution | < 10 min | Playwright report |
| System uptime | > 99.5% | Monitoring dashboard |
| Queue depth | < 100 | RabbitMQ console |

---

## 🎯 Phase Checklist

### Phase 0: Prerequisites (1-2 days)
- [ ] Docker, Python, Node.js installed
- [ ] Domoticz accessible
- [ ] Git configured

### Phase 1: Infrastructure (2-3 days)
- [ ] RabbitMQ running
- [ ] Domoticz API tested
- [ ] Directory structure created

### Phase 2: Playwright (2-3 days)
- [ ] Node.js project initialized
- [ ] Tests created
- [ ] Docker image builds

### Phase 3: Device Agent (2-3 days)
- [ ] Python environment setup
- [ ] Agent implemented
- [ ] Domoticz integration working

### Phase 4: Airflow (2-3 days)
- [ ] Services running
- [ ] DAGs created
- [ ] Manual trigger successful

### Phase 5: Jenkins (2-3 days)
- [ ] Pipeline created
- [ ] Build stages working
- [ ] Images pushed to registry

### Phase 6: Integration (3-4 days)
- [ ] Message flow tested
- [ ] End-to-end working
- [ ] Correlation IDs tracked

### Phase 7-11: Advanced (2-3 weeks)
- [ ] Real-time events
- [ ] Logging/monitoring
- [ ] Security hardening
- [ ] Production deployment

---

## 💡 Pro Tips

1. **Use correlation IDs** - Track messages end-to-end
2. **Enable persistence** - RabbitMQ queues survive restarts
3. **Set timeouts** - Prevent hanging requests
4. **Log everything** - Essential for debugging
5. **Test locally first** - Before deploying to production
6. **Monitor queues** - Prevent backlog buildup
7. **Use health checks** - Detect failures early
8. **Backup regularly** - Protect your data
9. **Document changes** - Keep team informed
10. **Automate testing** - Catch issues early

---

## 🚨 Emergency Procedures

### RabbitMQ Down
```bash
# Restart
docker-compose restart rabbitmq

# Check status
docker-compose logs rabbitmq

# Purge queue if needed
docker-compose exec rabbitmq rabbitmqctl purge_queue device_commands
```

### Airflow Stuck
```bash
# Clear task state
docker-compose exec airflow-webserver airflow tasks clear <dag_id>

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Device Agent Failing
```bash
# Check logs
docker-compose logs device-agent

# Restart
docker-compose restart device-agent

# Verify Domoticz connectivity
docker-compose exec device-agent curl http://domoticz:8080/json.htm?type=devices
```

---

## 📞 Getting Help

1. **Check TROUBLESHOOTING.md** - Most issues covered
2. **Review logs** - `docker-compose logs <service>`
3. **Check ARCHITECTURE.md** - Understand design
4. **Test connectivity** - Verify each component
5. **Consult TECHNICAL_SPECS.md** - Implementation details

---

## 📚 External Resources

- **RabbitMQ:** https://www.rabbitmq.com/documentation.html
- **Airflow:** https://airflow.apache.org/docs/
- **Playwright:** https://playwright.dev/
- **Domoticz:** https://www.domoticz.com/wiki/
- **Jenkins:** https://www.jenkins.io/doc/
- **Docker:** https://docs.docker.com/

---

## ✅ Success Indicators

- ✅ All services running and healthy
- ✅ No errors in logs
- ✅ Messages flowing through RabbitMQ
- ✅ DAGs executing on schedule
- ✅ Devices responding to commands
- ✅ Tests running and passing
- ✅ Jenkins pipeline working
- ✅ Monitoring and alerts active

---

**Last Updated:** 2024-01-15  
**Version:** 1.0  
**Status:** Ready to Use
