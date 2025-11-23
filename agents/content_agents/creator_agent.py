#!/usr/bin/env python3
"""
Content Creator Agent: Generates platform-specific content using OpenRouter (Grok 4.1).
Publishes content variants to RabbitMQ for Scheduler Agent.
"""

import os
import json
import logging
import requests
import pika
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentCreatorAgent:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.connection = None
        self.channel = None
    
    def connect_rabbitmq(self):
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'guest'),
            os.getenv('RABBITMQ_PASS', 'guest')
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'localhost'),
            credentials=credentials,
            heartbeat=600
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange='content', exchange_type='topic', durable=True)
        self.channel.queue_declare(queue='creation_requests', durable=True)
        self.channel.queue_bind(
            exchange='content',
            queue='creation_requests',
            routing_key='content.create.request'
        )
        logger.info("Connected to RabbitMQ")
    
    def create_twitter_content(self, article: str, campaign_plan: Dict) -> List[Dict[str, Any]]:
        try:
            topic = research_data.get('topic', 'Research')
            prompt = f"""
            Create a formal academic title for research on: {topic}
            Make it suitable for academic journals, clear and concise.
            Return only the title, no JSON.
            """
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                    'HTTP-Referer': 'http://localhost',
                    'X-Title': 'Content Creator Agent'
                },
                json={
                    'model': 'grok-2-1212',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.5
                }
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            return f"Research on {topic}"
        except Exception as e:
            logger.error(f"Title creation failed: {e}")
            return f"Research on {research_data.get('topic', 'Topic')}"

    def create_thai_abstract(self, research_data: Dict, title: str) -> str:
        """Create Thai abstract in IEEE format (Step 5)"""
        try:
            prompt = f"""
            Create a professional Thai abstract (บทคัดย่อภาษาไทย) in IEEE journal format for:
            Title: {title}
            
            Requirements:
            - 100-150 words
            - Academic tone
            - IEEE format
            - Include: objective, method, results, conclusion
            
            Return only the abstract in Thai.
            """
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                    'HTTP-Referer': 'http://localhost',
                    'X-Title': 'Content Creator Agent'
                },
                json={
                    'model': 'grok-2-1212',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.5
                }
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            return "บทคัดย่อ: งานวิจัยนี้ศึกษา..."
        except Exception as e:
            logger.error(f"Thai abstract creation failed: {e}")
            return "บทคัดย่อ: งานวิจัยนี้ศึกษา..."

    def summarize_paper(self, research_data: Dict) -> str:
        """Summarize paper content (Step 6)"""
        try:
            topic = research_data.get('topic', 'Research')
            prompt = f"""
            Create a comprehensive summary of research on: {topic}
            
            Include:
            - Key findings
            - Methodology
            - Significance
            - Future directions
            
            Keep it academic and formal.
            """
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                    'HTTP-Referer': 'http://localhost',
                    'X-Title': 'Content Creator Agent'
                },
                json={
                    'model': 'grok-2-1212',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.6
                }
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            return f"Summary of {topic} research"
        except Exception as e:
            logger.error(f"Paper summarization failed: {e}")
            return f"Summary of {research_data.get('topic', 'research')}"

    def convert_to_casual_style(self, academic_text: str) -> str:
        """Convert academic text to casual style (Step 7)"""
        try:
            prompt = f"""
            Convert this academic text to casual, engaging style suitable for Twitter:
            
            {academic_text[:500]}
            
            Make it:
            - Easy to understand
            - Engaging
            - Twitter-friendly
            - Keep the main message
            
            Return only the converted text.
            """
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                    'HTTP-Referer': 'http://localhost',
                    'X-Title': 'Content Creator Agent'
                },
                json={
                    'model': 'grok-2-1212',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7
                }
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            return academic_text[:280]
        except Exception as e:
            logger.error(f"Style conversion failed: {e}")
            return academic_text[:280]

    def create_content(self, article: str, platform: str, research_data: Dict = None) -> Dict[str, Any]:
        """Create platform-specific content following WORKFLOW.md (Steps 4-7)"""
        try:
            # Step 4: Create academic title
            title = self.create_academic_title(research_data or {})
            
            # Step 5: Create Thai abstract
            thai_abstract = self.create_thai_abstract(research_data or {}, title)
            
            # Step 6: Summarize paper
            summary = self.summarize_paper(research_data or {})
            
            # Step 7: Convert to casual style
            casual_content = self.convert_to_casual_style(summary)
            
            return {
                'title': title,
                'thai_abstract': thai_abstract,
                'summary': summary,
                'casual_content': casual_content,
                'platform': platform,
                'hashtags': ['research', 'academic', 'science'],
                'engagement_score': 0.85
            }
                
        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            return {
                'title': 'Research Article',
                'thai_abstract': 'บทคัดย่อ: งานวิจัยนี้...',
                'summary': article[:200],
                'casual_content': article[:280],
                'platform': platform,
                'hashtags': ['research'],
                'engagement_score': 0.3
            }
    
    def on_message(self, ch, method, properties, body):
        """Handle incoming content creation requests."""
        try:
            message = json.loads(body)
            correlation_id = message.get('correlation_id')
            article = message.get('article', '')
            campaign_plan = message.get('campaign_plan', {})
            platform = message.get('platform', 'twitter')
            
            logger.info(f"[{correlation_id}] Creating content for {platform}")
            
            if platform == 'twitter':
                result = self.create_twitter_content(article, campaign_plan)
            else:
                result = {'success': False, 'error': f'Unsupported platform: {platform}'}
            
            result['correlation_id'] = correlation_id
            result['timestamp'] = datetime.utcnow().isoformat()
            
            self.channel.basic_publish(
                exchange='content',
                routing_key='content.schedule.request',
                body=json.dumps(result),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
            )
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{correlation_id}] Content created, sent to scheduler")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """Start the content creator agent."""
        self.connect_rabbitmq()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='creation_requests', on_message_callback=self.on_message)
        logger.info("Content Creator Agent started. Waiting for requests...")
        self.channel.start_consuming()

if __name__ == '__main__':
    agent = ContentCreatorAgent()
    agent.start()
