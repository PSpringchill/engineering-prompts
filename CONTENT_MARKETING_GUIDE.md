# Content Creation & Marketing Automation Guide

## Quick Overview

Extend your multi-agent automation system with **AI-powered content generation and social media marketing**.

**Components:**
- **Researcher Agent** (Gemini API) - Gathers information
- **Editor Agent** (Gemini API) - Structures content
- **Writer Agent** (Gemini API) - Drafts articles
- **Strategist Agent** (Gemini API) - Plans campaigns
- **Creator Agent** (OpenRouter/Grok 4.1) - Generates social media content
- **Scheduler Agent** (Twitter API v2) - Posts to Twitter

---

## Setup

### 1. Install Dependencies

```bash
cd agents/content_agents
pip install -r requirements.txt
```

### 2. Configure Environment

Your `.env` already has:
```
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_BEARER_TOKEN=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...
```

### 3. Start Agents

```bash
# Terminal 1: Researcher Agent
python researcher_agent.py

# Terminal 2: Creator Agent
python creator_agent.py

# Terminal 3: Scheduler Agent
python scheduler_agent.py
```

Or with Docker:
```bash
docker-compose up researcher-agent creator-agent scheduler-agent
```

---

## Message Flow

### Content Generation Pipeline

```
Airflow DAG
    ↓
[Trigger Research Request]
    ↓
RabbitMQ: content.research.request
    ↓
Researcher Agent (Gemini)
    ↓
RabbitMQ: content.edit.request
    ↓
Editor Agent (Gemini)
    ↓
RabbitMQ: content.write.request
    ↓
Writer Agent (Gemini)
    ↓
Final Article → Database/Storage
```

### Campaign Execution Pipeline

```
Airflow DAG
    ↓
[Trigger Campaign Strategy]
    ↓
RabbitMQ: content.strategy.request
    ↓
Strategist Agent (Gemini)
    ↓
RabbitMQ: content.create.request
    ↓
Creator Agent (OpenRouter/Grok)
    ↓
RabbitMQ: content.schedule.request
    ↓
Scheduler Agent (Twitter API)
    ↓
Tweets Posted to Twitter
```

---

## API Usage & Costs

### Gemini API (Free Tier Available)
- **Researcher:** ~500 tokens per research
- **Editor:** ~300 tokens per outline
- **Writer:** ~1000 tokens per article
- **Free tier:** 60 requests/minute

### OpenRouter (Grok 4.1)
- **Creator:** ~200 tokens per tweet set
- **Cost:** ~$0.01-0.05 per request
- **Rate limit:** 100 requests/minute

### Twitter API v2
- **Scheduler:** 1 request per tweet
- **Free tier:** 450 requests/15 minutes
- **Cost:** Free (with rate limits)

---

## Example: Trigger Content Generation

```python
import pika
import json
import uuid

# Connect to RabbitMQ
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# Declare exchange
channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)

# Send research request
message = {
    'correlation_id': str(uuid.uuid4()),
    'topic': 'AI in Healthcare 2024',
    'keywords': ['AI', 'healthcare', 'diagnosis', 'machine learning'],
    'depth': 'comprehensive'
}

channel.basic_publish(
    exchange='content',
    routing_key='content.research.request',
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
)

print("✓ Research request sent")
connection.close()
```

---

## Example: Trigger Campaign

```python
import pika
import json
import uuid

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)

message = {
    'correlation_id': str(uuid.uuid4()),
    'campaign_name': 'Q1_AI_Awareness',
    'objective': 'increase_awareness',
    'target_audience': 'tech_professionals',
    'duration_days': 30,
    'platforms': ['twitter'],
    'content_themes': ['AI trends', 'machine learning', 'automation'],
    'posting_schedule': [
        {'day': 'monday', 'time': '09:00'},
        {'day': 'wednesday', 'time': '14:00'},
        {'day': 'friday', 'time': '10:00'}
    ]
}

channel.basic_publish(
    exchange='content',
    routing_key='content.strategy.request',
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
)

print("✓ Campaign strategy request sent")
connection.close()
```

---

## Monitoring

### Check RabbitMQ Queues

```bash
docker-compose exec rabbitmq rabbitmqctl list_queues name messages consumers

# Expected output:
# research_requests        0       1
# creation_requests        0       1
# schedule_requests        0       1
```

### View Agent Logs

```bash
docker-compose logs researcher-agent -f
docker-compose logs creator-agent -f
docker-compose logs scheduler-agent -f
```

### Monitor Twitter Posts

```bash
# Check posted tweets
curl -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" \
  "https://api.twitter.com/2/tweets/search/recent?query=from:your_handle"
```

---

## Troubleshooting

### Gemini API Errors

```
Error: API key not valid
→ Check GEMINI_API_KEY in .env
→ Verify key is active in Google Cloud Console
```

### OpenRouter Errors

```
Error: 401 Unauthorized
→ Check OPENROUTER_API_KEY in .env
→ Verify key has correct permissions
→ Check rate limits
```

### Twitter API Errors

```
Error: 401 Unauthorized
→ Verify all Twitter credentials in .env
→ Check token expiration
→ Verify account has write permissions
```

### RabbitMQ Connection Issues

```
Error: Connection refused
→ docker-compose restart rabbitmq
→ Verify RABBITMQ_HOST is correct
→ Check network connectivity
```

---

## Performance Optimization

### Parallel Processing

```python
# In Airflow DAG
from airflow.operators.python import PythonOperator

# Run multiple research tasks in parallel
research_task_1 = PythonOperator(task_id='research_topic_1', ...)
research_task_2 = PythonOperator(task_id='research_topic_2', ...)
research_task_3 = PythonOperator(task_id='research_topic_3', ...)

# All run in parallel
[research_task_1, research_task_2, research_task_3] >> editor_task
```

### Caching

```python
# Cache research results for same topic
import hashlib

def get_cache_key(topic, keywords):
    key = f"{topic}:{','.join(sorted(keywords))}"
    return hashlib.md5(key.encode()).hexdigest()

# Check cache before researching
cache_key = get_cache_key(topic, keywords)
if cache_key in research_cache:
    return research_cache[cache_key]
```

### Rate Limiting

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_api_with_retry():
    # API call with automatic retry
    pass
```

---

## Security Considerations

### 1. Rotate API Keys Immediately

Your `.env` was exposed. Rotate all keys:
- Google Cloud Console → Regenerate Gemini API key
- OpenRouter → Generate new API key
- Twitter Developer Portal → Regenerate tokens

### 2. Use Secrets Manager

```python
# Instead of .env, use Vault
from hvac import Client

vault = Client(url='https://vault.example.com')
secrets = vault.secrets.kv.read_secret_version(path='automation/apis')
gemini_key = secrets['data']['data']['gemini_api_key']
```

### 3. Audit Logging

```python
# Log all API calls
logger.info(f"[{correlation_id}] API call: {api_name}, tokens: {token_count}")
```

---

## Cost Estimation (Monthly)

| Service | Requests | Cost |
|---------|----------|------|
| Gemini API | 1000 | Free (free tier) |
| OpenRouter | 500 | ~$5-10 |
| Twitter API | 5000 | Free |
| RabbitMQ | Unlimited | $0 (self-hosted) |
| **Total** | | **~$5-10/month** |

---

## Next Steps

1. **Test locally** - Run agents and trigger requests
2. **Monitor performance** - Check logs and metrics
3. **Optimize prompts** - Improve content quality
4. **Scale up** - Add more agents/workers
5. **Integrate with Airflow** - Automate scheduling
6. **Monitor Twitter** - Track engagement metrics

---

## Files Created

- `agents/content_agents/researcher_agent.py` - Researcher implementation
- `agents/content_agents/creator_agent.py` - Creator implementation
- `agents/content_agents/scheduler_agent.py` - Scheduler implementation
- `agents/content_agents/requirements.txt` - Python dependencies
- `agents/content_agents/Dockerfile` - Docker configuration

---

**Status:** Ready to deploy  
**Last Updated:** 2024-01-15
