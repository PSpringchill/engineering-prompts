"""
Content Generation DAG - Automates the research, editing, and writing process
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import pika
import json
import uuid
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'content_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

def send_research_request(topic, keywords, **context):
    """Send research request to Researcher Agent"""
    try:
        correlation_id = str(uuid.uuid4())
        
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq', credentials=credentials, heartbeat=600
        ))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)
        
        message = {
            'correlation_id': correlation_id,
            'topic': topic,
            'keywords': keywords,
            'depth': 'comprehensive'
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.research.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Research request sent for topic: {topic}")
        return {'correlation_id': correlation_id, 'status': 'sent'}
        
    except Exception as e:
        logger.error(f"Failed to send research request: {e}")
        raise

def send_content_creation_request(article, campaign_theme, **context):
    """Send content creation request to Creator Agent"""
    try:
        correlation_id = str(uuid.uuid4())
        
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq', credentials=credentials, heartbeat=600
        ))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)
        
        message = {
            'correlation_id': correlation_id,
            'article': article,
            'campaign_plan': {
                'target_audience': 'tech_professionals',
                'content_themes': [campaign_theme]
            },
            'platform': 'twitter'
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.create.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Content creation request sent")
        return {'correlation_id': correlation_id, 'status': 'sent'}
        
    except Exception as e:
        logger.error(f"Failed to send content creation request: {e}")
        raise

def send_scheduling_request(tweets, **context):
    """Send scheduling request to Scheduler Agent"""
    try:
        correlation_id = str(uuid.uuid4())
        
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq', credentials=credentials, heartbeat=600
        ))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)
        
        message = {
            'correlation_id': correlation_id,
            'tweets': tweets
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.schedule.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Scheduling request sent for {len(tweets)} tweets")
        return {'correlation_id': correlation_id, 'status': 'sent', 'tweet_count': len(tweets)}
        
    except Exception as e:
        logger.error(f"Failed to send scheduling request: {e}")
        raise

# Define the DAG
with DAG(
    'content_generation_dag',
    default_args=default_args,
    description='Automate content generation: Research → Create → Schedule',
    schedule_interval='0 9 * * 1',  # Every Monday at 9 AM
    catchup=False,
    tags=['content', 'automation'],
) as dag:
    
    # Task 1: Send research request
    research_task = PythonOperator(
        task_id='send_research_request',
        python_callable=send_research_request,
        op_kwargs={
            'topic': 'Latest Technology Trends 2024',
            'keywords': ['AI', 'machine learning', 'automation', 'cloud computing', 'blockchain']
        },
    )
    
    # Task 2: Send content creation request
    create_content_task = PythonOperator(
        task_id='send_content_creation_request',
        python_callable=send_content_creation_request,
        op_kwargs={
            'article': 'Latest technology trends are reshaping the industry with AI, machine learning, and automation leading the way.',
            'campaign_theme': 'Technology Innovation'
        },
    )
    
    # Task 3: Send scheduling request with sample tweets
    schedule_tweets_task = PythonOperator(
        task_id='send_scheduling_request',
        python_callable=send_scheduling_request,
        op_kwargs={
            'tweets': [
                {'content': 'AI and machine learning are transforming industries! 🚀 #AI #Tech #Innovation'},
                {'content': 'Cloud computing and automation are the future of enterprise IT. #Cloud #DevOps'},
                {'content': 'Blockchain technology continues to evolve with new use cases emerging. #Blockchain #Web3'}
            ]
        },
    )
    
    # Define task dependencies
    research_task >> create_content_task >> schedule_tweets_task
