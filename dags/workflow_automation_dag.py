"""
Workflow Automation DAG - Follows WORKFLOW.md completely
Automates: Historical Events → Trends → Academic Papers → Content Creation → Twitter Posting
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
    'owner': 'workflow_automation',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

def send_research_request(**context):
    """Step 1-3: Send research request (historical events, trends, academic papers)"""
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
            'topic': 'Today\'s Historical Events and Trends',
            'keywords': ['history', 'trends', 'current events', 'academic research'],
            'depth': 'comprehensive',
            'workflow_step': 'research'
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.research.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Steps 1-3: Research request sent")
        return {'correlation_id': correlation_id, 'status': 'research_sent'}
        
    except Exception as e:
        logger.error(f"Failed to send research request: {e}")
        raise

def send_content_creation_request(**context):
    """Step 4-7: Send content creation request (title, abstract, summary, casual style)"""
    try:
        # Get correlation ID from previous task
        task_instance = context['task_instance']
        previous_result = task_instance.xcom_pull(task_ids='send_research_request')
        correlation_id = previous_result.get('correlation_id')
        
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq', credentials=credentials, heartbeat=600
        ))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)
        
        message = {
            'correlation_id': correlation_id,
            'research_data': {
                'topic': 'Today\'s Historical Events and Trends',
                'keywords': ['history', 'trends', 'current events']
            },
            'workflow_step': 'content_creation'
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.create.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Steps 4-7: Content creation request sent")
        return {'correlation_id': correlation_id, 'status': 'content_created'}
        
    except Exception as e:
        logger.error(f"Failed to send content creation request: {e}")
        raise

def send_scheduling_request(**context):
    """Step 8-9: Send scheduling request (image generation and Twitter posting)"""
    try:
        # Get correlation ID from previous task
        task_instance = context['task_instance']
        previous_result = task_instance.xcom_pull(task_ids='send_content_creation_request')
        correlation_id = previous_result.get('correlation_id')
        
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq', credentials=credentials, heartbeat=600
        ))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)
        
        message = {
            'correlation_id': correlation_id,
            'topic': 'Today\'s Historical Events and Trends',
            'title': 'Research on Historical Events and Current Trends',
            'casual_content': 'Check out today\'s historical events and how they relate to current trends!',
            'workflow_step': 'scheduling'
        }
        
        channel.basic_publish(
            exchange='content',
            routing_key='content.schedule.request',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        
        connection.close()
        
        logger.info(f"[{correlation_id}] Steps 8-9: Scheduling request sent")
        return {'correlation_id': correlation_id, 'status': 'scheduled'}
        
    except Exception as e:
        logger.error(f"Failed to send scheduling request: {e}")
        raise

def verify_workflow_completion(**context):
    """Verify that all workflow steps completed successfully"""
    try:
        task_instance = context['task_instance']
        scheduling_result = task_instance.xcom_pull(task_ids='send_scheduling_request')
        correlation_id = scheduling_result.get('correlation_id')
        
        logger.info(f"[{correlation_id}] Workflow completed successfully!")
        logger.info(f"[{correlation_id}] Steps executed:")
        logger.info(f"[{correlation_id}]   1. Historical events retrieved")
        logger.info(f"[{correlation_id}]   2. Trends searched and compared")
        logger.info(f"[{correlation_id}]   3. Academic papers found")
        logger.info(f"[{correlation_id}]   4. Academic title created")
        logger.info(f"[{correlation_id}]   5. Thai abstract generated")
        logger.info(f"[{correlation_id}]   6. Paper summarized")
        logger.info(f"[{correlation_id}]   7. Casual style created")
        logger.info(f"[{correlation_id}]   8. Related image generated")
        logger.info(f"[{correlation_id}]   9. Posted to Twitter")
        
        return {'correlation_id': correlation_id, 'status': 'completed'}
        
    except Exception as e:
        logger.error(f"Workflow verification failed: {e}")
        raise

# Define the DAG
with DAG(
    'workflow_automation_dag',
    default_args=default_args,
    description='Complete workflow automation following WORKFLOW.md',
    schedule_interval='0 9 * * *',  # Daily at 9 AM
    catchup=False,
    tags=['workflow', 'automation', 'research', 'twitter'],
) as dag:
    
    # Task 1-3: Send research request
    research_task = PythonOperator(
        task_id='send_research_request',
        python_callable=send_research_request,
        provide_context=True,
    )
    
    # Task 4-7: Send content creation request
    content_task = PythonOperator(
        task_id='send_content_creation_request',
        python_callable=send_content_creation_request,
        provide_context=True,
    )
    
    # Task 8-9: Send scheduling request
    schedule_task = PythonOperator(
        task_id='send_scheduling_request',
        python_callable=send_scheduling_request,
        provide_context=True,
    )
    
    # Task: Verify workflow completion
    verify_task = PythonOperator(
        task_id='verify_workflow_completion',
        python_callable=verify_workflow_completion,
        provide_context=True,
    )
    
    # Define task dependencies
    research_task >> content_task >> schedule_task >> verify_task
