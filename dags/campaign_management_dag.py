"""
Campaign Management DAG - Automates marketing campaign execution
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
    'owner': 'marketing_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

def send_strategy_request(campaign_name, objective, **context):
    """Send campaign strategy request to Strategist Agent"""
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
            'campaign_name': campaign_name,
            'objective': objective,
            'target_audience': 'tech_professionals',
            'duration_days': 30,
            'platforms': ['twitter']
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.strategy.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Campaign strategy request sent: {campaign_name}")
        return {'correlation_id': correlation_id, 'status': 'sent'}
        
    except Exception as e:
        logger.error(f"Failed to send strategy request: {e}")
        raise

def send_campaign_content_request(campaign_name, **context):
    """Send campaign content creation request"""
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
            'campaign_name': campaign_name,
            'content_type': 'social_media',
            'platforms': ['twitter'],
            'quantity': 5
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.campaign.create',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Campaign content request sent")
        return {'correlation_id': correlation_id, 'status': 'sent'}
        
    except Exception as e:
        logger.error(f"Failed to send campaign content request: {e}")
        raise

def monitor_campaign_performance(campaign_name, **context):
    """Monitor campaign performance metrics"""
    try:
        logger.info(f"Monitoring campaign: {campaign_name}")
        
        # In a real scenario, this would fetch metrics from Twitter API
        # For now, we'll just log the monitoring action
        metrics = {
            'impressions': 0,
            'engagements': 0,
            'clicks': 0,
            'conversions': 0
        }
        
        logger.info(f"Campaign metrics: {metrics}")
        return {'campaign': campaign_name, 'metrics': metrics}
        
    except Exception as e:
        logger.error(f"Failed to monitor campaign: {e}")
        raise

# Define the DAG
with DAG(
    'campaign_management_dag',
    default_args=default_args,
    description='Automate marketing campaign: Strategy → Create → Monitor',
    schedule_interval='0 10 * * 1',  # Every Monday at 10 AM
    catchup=False,
    tags=['marketing', 'campaign'],
) as dag:
    
    # Task 1: Send campaign strategy request
    strategy_task = PythonOperator(
        task_id='send_strategy_request',
        python_callable=send_strategy_request,
        op_kwargs={
            'campaign_name': 'Q4_2024_Tech_Campaign',
            'objective': 'increase_awareness'
        },
    )
    
    # Task 2: Send campaign content creation request
    content_task = PythonOperator(
        task_id='send_campaign_content_request',
        python_callable=send_campaign_content_request,
        op_kwargs={
            'campaign_name': 'Q4_2024_Tech_Campaign'
        },
    )
    
    # Task 3: Monitor campaign performance
    monitor_task = PythonOperator(
        task_id='monitor_campaign_performance',
        python_callable=monitor_campaign_performance,
        op_kwargs={
            'campaign_name': 'Q4_2024_Tech_Campaign'
        },
    )
    
    # Define task dependencies
    strategy_task >> content_task >> monitor_task
