# Troubleshooting Guide

## Common Issues & Solutions

### RabbitMQ Issues

#### Issue: "Connection refused" when connecting to RabbitMQ

**Symptoms:**
```
pika.exceptions.AMQPConnectionError: Connection refused
```

**Diagnosis:**
```bash
# Check if RabbitMQ is running
docker-compose ps rabbitmq

# Check RabbitMQ logs
docker-compose logs rabbitmq

# Test connectivity
docker-compose exec rabbitmq rabbitmq-diagnostics ping
```

**Solutions:**
1. **RabbitMQ not started:**
   ```bash
   docker-compose up -d rabbitmq
   docker-compose logs -f rabbitmq  # Wait for startup
   ```

2. **Port conflict:**
   ```bash
   # Check if port 5672 is in use
   lsof -i :5672
   
   # Change port in docker-compose.yml if needed
   ```

3. **Network isolation:**
   ```bash
   # Verify network connectivity
   docker network ls
   docker network inspect automation_automation
   
   # Ensure all services use same network
   ```

4. **Credentials incorrect:**
   ```bash
   # Verify credentials in .env and docker-compose.yml match
   # Default: guest/guest
   ```

---

#### Issue: Messages not being consumed

**Symptoms:**
- Messages published but not processed
- Queue depth increasing indefinitely
- Device commands not executed

**Diagnosis:**
```bash
# Check queue status
docker-compose exec rabbitmq rabbitmqctl list_queues name messages consumers

# Check bindings
docker-compose exec rabbitmq rabbitmqctl list_bindings

# Check exchange status
docker-compose exec rabbitmq rabbitmqctl list_exchanges
```

**Solutions:**
1. **Consumer not running:**
   ```bash
   docker-compose logs device-agent
   docker-compose ps device-agent
   
   # Restart if needed
   docker-compose restart device-agent
   ```

2. **Queue not bound to exchange:**
   ```bash
   # Verify binding in agent code
   # Check routing key matches publisher
   ```

3. **Consumer crashed:**
   ```bash
   # Check logs for errors
   docker-compose logs device-agent --tail=100
   
   # Check if process is running
   docker-compose exec device-agent ps aux
   ```

4. **Prefetch limit reached:**
   ```python
   # In agent.py, verify prefetch count
   channel.basic_qos(prefetch_count=1)  # Adjust if needed
   ```

---

#### Issue: RabbitMQ memory usage growing

**Symptoms:**
- RabbitMQ container using excessive memory
- Performance degradation
- Out of memory errors

**Diagnosis:**
```bash
# Check memory usage
docker stats rabbitmq

# Check queue sizes
docker-compose exec rabbitmq rabbitmqctl list_queues name messages

# Check for unacknowledged messages
docker-compose exec rabbitmq rabbitmqctl list_queues name messages consumers
```

**Solutions:**
1. **Purge old messages:**
   ```bash
   docker-compose exec rabbitmq rabbitmqctl purge_queue device_commands
   ```

2. **Set memory limits in docker-compose.yml:**
   ```yaml
   rabbitmq:
     environment:
       RABBITMQ_VM_MEMORY_HIGH_WATERMARK: 512MB
   ```

3. **Enable message TTL:**
   ```python
   # In agent.py
   channel.basic_publish(
       ...,
       properties=pika.BasicProperties(
           expiration='3600000'  # 1 hour in milliseconds
       )
   )
   ```

---

### Device Agent Issues

#### Issue: Device Agent can't connect to Domoticz

**Symptoms:**
```
Failed to get device status for idx 1: Connection refused
```

**Diagnosis:**
```bash
# Check Domoticz is running
curl http://localhost:8081/json.htm?type=devices

# Check Device Agent logs
docker-compose logs device-agent

# Test from Device Agent container
docker-compose exec device-agent curl http://domoticz:8080/json.htm?type=devices
```

**Solutions:**
1. **Domoticz not running:**
   ```bash
   # Start Domoticz
   docker-compose up -d domoticz
   
   # Or verify external Domoticz is accessible
   curl http://your-domoticz-host:8080/json.htm?type=devices
   ```

2. **Wrong URL in environment:**
   ```bash
   # Check DOMOTICZ_URL in docker-compose.yml
   # Should be http://domoticz:8080 (internal) or http://host:port (external)
   
   docker-compose logs device-agent | grep DOMOTICZ
   ```

3. **Network connectivity:**
   ```bash
   # Test from Device Agent container
   docker-compose exec device-agent ping domoticz
   docker-compose exec device-agent curl -v http://domoticz:8080/json.htm?type=devices
   ```

4. **Firewall/Security:**
   ```bash
   # Check if Domoticz API is protected
   # Verify API key if required
   # Check CORS settings
   ```

---

#### Issue: Device commands not executing

**Symptoms:**
- Device Agent receives message
- No error in logs
- Device doesn't toggle

**Diagnosis:**
```bash
# Check device exists in Domoticz
curl "http://localhost:8081/json.htm?type=devices&rid=1"

# Check device type
# Verify device is controllable (not read-only)

# Check Device Agent logs
docker-compose logs device-agent | grep "idx=1"
```

**Solutions:**
1. **Invalid device ID:**
   ```bash
   # List all devices
   curl "http://localhost:8081/json.htm?type=devices"
   
   # Use correct idx from response
   ```

2. **Device not controllable:**
   ```bash
   # Some devices are read-only (sensors)
   # Verify device type supports switching
   # Check Domoticz device settings
   ```

3. **API authentication required:**
   ```python
   # In agent.py, add authentication
   url = f"{DOMOTICZ_URL}/json.htm?type=command&param=switchlight&idx={idx}&switchcmd={action}&username=user&password=pass"
   ```

4. **Timeout:**
   ```python
   # Increase timeout in agent.py
   response = requests.get(url, timeout=30)  # Increase from 10
   ```

---

### Airflow Issues

#### Issue: DAG not appearing in Airflow UI

**Symptoms:**
- DAG file created but not visible
- "No DAGs found" message

**Diagnosis:**
```bash
# Check DAG syntax
python -m py_compile dags/device_automation_dag.py

# Check Airflow logs
docker-compose logs airflow-scheduler

# Verify DAG folder
docker-compose exec airflow-webserver ls -la /opt/airflow/dags/

# Check Airflow configuration
docker-compose exec airflow-webserver airflow config get-value core dags_folder
```

**Solutions:**
1. **DAG syntax error:**
   ```bash
   # Fix Python syntax errors
   python -m py_compile dags/device_automation_dag.py
   
   # Check for import errors
   docker-compose exec airflow-webserver python -c "from dags.device_automation_dag import dag"
   ```

2. **DAG not in correct folder:**
   ```bash
   # Verify dags/ folder is mounted
   docker-compose exec airflow-webserver ls -la /opt/airflow/dags/
   
   # Check docker-compose.yml volumes
   ```

3. **DAG parsing disabled:**
   ```bash
   # Check Airflow configuration
   docker-compose exec airflow-webserver airflow config get-value core load_examples
   
   # Force DAG refresh
   docker-compose exec airflow-webserver airflow dags list
   ```

4. **Scheduler not running:**
   ```bash
   docker-compose ps airflow-scheduler
   docker-compose logs airflow-scheduler
   
   # Restart if needed
   docker-compose restart airflow-scheduler
   ```

---

#### Issue: DAG task fails with "Connection refused"

**Symptoms:**
```
PythonOperator task fails
pika.exceptions.AMQPConnectionError: Connection refused
```

**Diagnosis:**
```bash
# Check task logs in Airflow UI
# Or via CLI:
docker-compose exec airflow-webserver airflow tasks logs device_automation_dag turn_on_device 2024-01-15

# Check RabbitMQ connectivity from Airflow
docker-compose exec airflow-webserver python -c "import pika; pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))"
```

**Solutions:**
1. **RabbitMQ not accessible from Airflow:**
   ```bash
   # Verify network connectivity
   docker-compose exec airflow-webserver ping rabbitmq
   
   # Check if RabbitMQ is running
   docker-compose ps rabbitmq
   ```

2. **Hostname resolution issue:**
   ```bash
   # In DAG, use service name: 'rabbitmq'
   # Not 'localhost' or IP address
   
   parameters = pika.ConnectionParameters(
       host='rabbitmq',  # Use service name
       credentials=credentials,
   )
   ```

3. **Credentials mismatch:**
   ```bash
   # Verify credentials in DAG match RabbitMQ
   # Check docker-compose.yml environment variables
   ```

---

#### Issue: Airflow webserver won't start

**Symptoms:**
```
Container exits immediately
Health check fails
```

**Diagnosis:**
```bash
# Check logs
docker-compose logs airflow-webserver

# Check database
docker-compose exec airflow-webserver airflow db check

# Check permissions
docker-compose exec airflow-webserver ls -la /opt/airflow/
```

**Solutions:**
1. **Database not initialized:**
   ```bash
   docker-compose exec airflow-webserver airflow db init
   docker-compose exec airflow-webserver airflow users create \
     --username airflow \
     --password airflow \
     --firstname Air \
     --lastname Flow \
     --role Admin \
     --email airflow@example.com
   ```

2. **Permission issues:**
   ```bash
   # Fix ownership
   docker-compose exec airflow-webserver chown -R airflow:airflow /opt/airflow
   ```

3. **Port conflict:**
   ```bash
   # Check if port 8080 is in use
   lsof -i :8080
   
   # Change port in docker-compose.yml if needed
   ```

---

### Playwright Agent Issues

#### Issue: Tests fail with "Browser not found"

**Symptoms:**
```
Error: Executable doesn't exist at /ms-playwright/chromium-*/chrome-linux/chrome
```

**Diagnosis:**
```bash
# Check if Playwright is installed
docker-compose exec ui-agent npx playwright --version

# Check browsers installed
docker-compose exec ui-agent npx playwright install --list
```

**Solutions:**
1. **Browsers not installed in Docker image:**
   ```dockerfile
   # In Dockerfile, ensure:
   RUN npx playwright install --with-deps
   ```

2. **Rebuild Docker image:**
   ```bash
   docker-compose build --no-cache ui-agent
   ```

3. **Missing system dependencies:**
   ```dockerfile
   # Add to Dockerfile if needed:
   RUN apt-get update && apt-get install -y \
       libglib2.0-0 \
       libx11-6 \
       libxext6 \
       libxrender1
   ```

---

#### Issue: Tests timeout

**Symptoms:**
```
Test timeout after 30000ms
Page.goto: Timeout 30000ms exceeded
```

**Diagnosis:**
```bash
# Check test configuration
cat agents/ui_agent/playwright.config.ts

# Check network connectivity
docker-compose exec ui-agent curl -v https://example.com

# Check test logs
docker-compose logs ui-agent
```

**Solutions:**
1. **Increase timeout in config:**
   ```typescript
   // In playwright.config.ts
   use: {
     navigationTimeout: 60000,
     actionTimeout: 30000,
   },
   ```

2. **Increase test timeout:**
   ```typescript
   test.setTimeout(60000);
   ```

3. **Network issues:**
   ```bash
   # Test connectivity from container
   docker-compose exec ui-agent ping example.com
   docker-compose exec ui-agent curl -I https://example.com
   ```

4. **Slow application:**
   ```typescript
   // Add wait conditions
   await page.waitForLoadState('networkidle');
   ```

---

#### Issue: Screenshots not captured

**Symptoms:**
- Test fails but no screenshot
- Screenshot directory empty

**Diagnosis:**
```bash
# Check screenshot directory
docker-compose exec ui-agent ls -la test-results/screenshots/

# Check Playwright config
grep -A5 "screenshot" agents/ui_agent/playwright.config.ts
```

**Solutions:**
1. **Screenshot not configured:**
   ```typescript
   // In playwright.config.ts
   use: {
     screenshot: 'only-on-failure',
   },
   ```

2. **Directory not mounted:**
   ```yaml
   # In docker-compose.yml
   volumes:
     - ./agents/ui_agent/test-results:/app/test-results
   ```

3. **Permissions issue:**
   ```bash
   # Check directory permissions
   ls -la agents/ui_agent/test-results/
   
   # Fix if needed
   chmod 777 agents/ui_agent/test-results/
   ```

---

### Jenkins Issues

#### Issue: Jenkins can't access Docker socket

**Symptoms:**
```
docker: Cannot connect to Docker daemon
```

**Diagnosis:**
```bash
# Check Docker socket permissions
ls -la /var/run/docker.sock

# Check Jenkins user
id jenkins

# Test Docker access
sudo -u jenkins docker ps
```

**Solutions:**
1. **Add Jenkins to docker group:**
   ```bash
   sudo usermod -aG docker jenkins
   sudo systemctl restart jenkins
   ```

2. **Fix socket permissions:**
   ```bash
   sudo chmod 666 /var/run/docker.sock
   ```

3. **Use TCP socket instead:**
   ```groovy
   // In Jenkinsfile
   docker_url = 'tcp://localhost:2375'
   ```

---

#### Issue: Pipeline fails to push to registry

**Symptoms:**
```
denied: requested access to the resource is denied
```

**Diagnosis:**
```bash
# Check credentials
jenkins-cli get-credentials system::system::jenkins

# Test login manually
echo $PASSWORD | docker login -u $USERNAME --password-stdin registry.example.com
```

**Solutions:**
1. **Invalid credentials:**
   ```bash
   # Update Jenkins credentials
   # Manage Jenkins > Manage Credentials > Add credentials
   ```

2. **Registry authentication:**
   ```groovy
   // In Jenkinsfile
   sh '''
     echo $REGISTRY_PASS | docker login -u $REGISTRY_USER --password-stdin ${REGISTRY}
   '''
   ```

3. **Image tag incorrect:**
   ```groovy
   // Ensure tag matches registry format
   image = "${REGISTRY}/${IMAGE_PREFIX}/ui-agent:${BUILD_TAG}"
   ```

---

### Docker Compose Issues

#### Issue: "docker-compose: command not found"

**Symptoms:**
```
bash: docker-compose: command not found
```

**Solutions:**
```bash
# Install Docker Compose v2
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Or use docker compose (v2 built-in)
docker compose up -d
```

---

#### Issue: "No space left on device"

**Symptoms:**
```
Error response from daemon: write /var/lib/docker/...: no space left on device
```

**Solutions:**
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove old images
docker image prune -a

# Check specific service
docker-compose exec rabbitmq du -sh /var/lib/rabbitmq
```

---

## Performance Tuning

### RabbitMQ Optimization

```bash
# Increase memory limit
docker-compose exec rabbitmq rabbitmqctl set_vm_memory_high_watermark 0.6

# Tune prefetch
# In agent.py:
channel.basic_qos(prefetch_count=10)  # Increase from 1 for higher throughput

# Enable lazy queue
channel.queue_declare(
    queue='device_commands',
    durable=True,
    arguments={'x-queue-mode': 'lazy'}
)
```

### Airflow Optimization

```bash
# Increase parallelism
# In docker-compose.yml:
AIRFLOW__CORE__PARALLELISM: 32
AIRFLOW__CORE__DAG_CONCURRENCY: 16

# Use CeleryExecutor for production
AIRFLOW__CORE__EXECUTOR: CeleryExecutor
```

### Playwright Optimization

```typescript
// In playwright.config.ts
workers: 4,  // Parallel workers
fullyParallel: true,  // Run tests in parallel
```

---

## Monitoring & Debugging

### Enable Debug Logging

```bash
# Device Agent
docker-compose logs device-agent -f | grep -i error

# Airflow
docker-compose exec airflow-webserver airflow config get-value logging logging_level

# RabbitMQ
docker-compose exec rabbitmq rabbitmqctl status
```

### Health Checks

```bash
# RabbitMQ
curl http://localhost:15672/api/aliveness-test/% -u guest:guest

# Airflow
curl http://localhost:8080/health

# Domoticz
curl http://localhost:8081/json.htm?type=command&param=getversion
```

### Performance Metrics

```bash
# Container stats
docker stats

# RabbitMQ metrics
docker-compose exec rabbitmq rabbitmqctl status

# Airflow metrics
docker-compose exec airflow-webserver airflow dags list-runs
```

---

**Last Updated:** 2024-01-15
