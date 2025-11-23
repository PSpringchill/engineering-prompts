# Content Marketing System - Quick Start (5 Minutes)

## 🚀 Fastest Setup

### Step 1: Verify Environment (1 min)
```bash
# Check all API keys are set
grep -E "GEMINI|OPENROUTER|TWITTER" /Users/studiomac/Documents/Code/engineering-prompts/.env

# Should show:
# GEMINI_API_KEY=...
# OPENROUTER_API_KEY=...
# TWITTER_API_KEY=...
# TWITTER_BEARER_TOKEN=...
# etc.
```

### Step 2: Install Dependencies (2 min)
```bash
cd /Users/studiomac/Documents/Code/engineering-prompts/agents/content_agents
pip install -r requirements.txt
```

### Step 3: Start Agents (1 min)
```bash
# Terminal 1
python researcher_agent.py

# Terminal 2 (new terminal)
python creator_agent.py

# Terminal 3 (new terminal)
python scheduler_agent.py
```

### Step 4: Test (1 min)
```bash
# Terminal 4 (new terminal)
python << 'EOF'
import pika, json, uuid

conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
ch = conn.channel()
ch.exchange_declare(exchange='content', exchange_type='topic', durable=True)

msg = {
    'correlation_id': str(uuid.uuid4()),
    'topic': 'AI in Healthcare',
    'keywords': ['AI', 'healthcare', 'diagnosis'],
    'depth': 'comprehensive'
}

ch.basic_publish(
    exchange='content',
    routing_key='content.research.request',
    body=json.dumps(msg),
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
)
print("✓ Research request sent!")
conn.close()
EOF
```

**Done!** Check Terminal 1 for research results.

---

## 📊 What Each Agent Does

| Agent | Input | Output | API |
|-------|-------|--------|-----|
| **Researcher** | Topic + keywords | Research data | Gemini |
| **Creator** | Article + campaign | Twitter posts | OpenRouter/Grok |
| **Scheduler** | Tweets | Posted to Twitter | Twitter API |

---

## 🔄 Message Topics

```
content.research.request     → Researcher Agent
content.edit.request         → Editor Agent
content.write.request        → Writer Agent
content.create.request       → Creator Agent
content.schedule.request     → Scheduler Agent
```

---

## 💡 Example: Generate Article & Post to Twitter

```bash
python << 'EOF'
import pika, json, uuid, time

conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
ch = conn.channel()
ch.exchange_declare(exchange='content', exchange_type='topic', durable=True)

correlation_id = str(uuid.uuid4())

# Step 1: Request research
print(f"[{correlation_id}] Requesting research...")
ch.basic_publish(
    exchange='content',
    routing_key='content.research.request',
    body=json.dumps({
        'correlation_id': correlation_id,
        'topic': 'Machine Learning Trends 2024',
        'keywords': ['ML', 'AI', 'trends', 'automation'],
        'depth': 'comprehensive'
    }),
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
)

# Wait for processing
time.sleep(5)

# Step 2: Request content creation
print(f"[{correlation_id}] Requesting content creation...")
ch.basic_publish(
    exchange='content',
    routing_key='content.create.request',
    body=json.dumps({
        'correlation_id': correlation_id,
        'article': 'Machine Learning is transforming industries...',
        'campaign_plan': {
            'target_audience': 'tech_professionals',
            'content_themes': ['ML trends', 'automation', 'AI']
        },
        'platform': 'twitter'
    }),
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
)

# Wait for processing
time.sleep(5)

# Step 3: Request scheduling
print(f"[{correlation_id}] Requesting tweet scheduling...")
ch.basic_publish(
    exchange='content',
    routing_key='content.schedule.request',
    body=json.dumps({
        'correlation_id': correlation_id,
        'tweets': [
            {'content': 'ML is revolutionizing tech! 🚀 #AI #MachineLearning'},
            {'content': 'Automation through ML: The future is here. #Tech #Innovation'}
        ]
    }),
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
)

print(f"[{correlation_id}] ✓ All requests sent!")
conn.close()
EOF
```

---

## 🐳 Docker Setup (Alternative)

```bash
# Add to docker-compose.yml (see DOCKER_COMPOSE_CONTENT_UPDATE.yml)
# Then:

docker-compose up researcher-agent creator-agent scheduler-agent

# View logs
docker-compose logs -f researcher-agent
docker-compose logs -f creator-agent
docker-compose logs -f scheduler-agent
```

---

## 🔍 Verify It's Working

```bash
# Check RabbitMQ queues
docker-compose exec rabbitmq rabbitmqctl list_queues

# Should show:
# research_requests        0       1
# creation_requests        0       1
# schedule_requests        0       1

# Check agent logs
docker-compose logs researcher-agent | tail -20
```

---

## 🚨 Security: Rotate API Keys NOW

Your `.env` was exposed. **Immediately:**

1. **Google Cloud Console**
   - Go to API Keys
   - Delete old Gemini key
   - Create new key
   - Update `.env`

2. **OpenRouter**
   - Account Settings → API Keys
   - Delete old key
   - Create new key
   - Update `.env`

3. **Twitter Developer Portal**
   - Keys & Tokens
   - Regenerate all tokens
   - Update `.env`

4. **Commit safely**
   ```bash
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "Add .env to gitignore"
   ```

---

## 📈 Monitor Performance

```bash
# Watch agent activity
watch -n 1 'docker-compose exec rabbitmq rabbitmqctl list_queues'

# Check Twitter posts
curl -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" \
  "https://api.twitter.com/2/tweets/search/recent?query=from:your_handle" | jq
```

---

## 🆘 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'pika'` | `pip install -r requirements.txt` |
| `Connection refused` | Ensure RabbitMQ is running: `docker-compose up rabbitmq` |
| `API key not valid` | Check .env, regenerate key in API console |
| `Twitter auth failed` | Verify all Twitter credentials, check token expiration |
| `Timeout` | Increase timeout in agent code, check API status |

---

## 📚 Full Documentation

- **CONTENT_MARKETING_GUIDE.md** - Complete setup & usage
- **CONTENT_MARKETING_SYSTEM.md** - Architecture & specs
- **CONTENT_MARKETING_SUMMARY.md** - Overview & next steps

---

## ✅ Checklist

- [ ] Verify API keys in .env
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start agents (3 terminals)
- [ ] Send test request
- [ ] Verify RabbitMQ queues
- [ ] Check agent logs
- [ ] Rotate API keys
- [ ] Add .env to .gitignore

---

**Time to first content:** ~5 minutes  
**Status:** Ready to use  
**Cost:** Free (Gemini free tier) + ~$0.01-0.05 per OpenRouter request
