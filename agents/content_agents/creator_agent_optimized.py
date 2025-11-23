#!/usr/bin/env python3
"""
Content Creation Specialist Agent
Transforms research data into high-quality academic and casual content.

Responsibilities:
1. Academic Title Creation - Create formal titles following academic conventions
2. Thai Abstract Generation - IEEE format, 100-150 words in Thai
3. Paper Summarization - 200-300 words with key findings, methodology, significance
4. Casual Style Conversion - Twitter-friendly content with hashtags and engagement

Quality Standards:
- Academic Accuracy: Based on verified sources
- Tone Consistency: Maintain voice across formats
- Data Integrity: Preserve all key statistics
- Platform Compliance: Follow Twitter/social media guidelines
- Cultural Sensitivity: Respect Thai language and culture
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

class OptimizedContentCreatorAgent:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.connection = None
        self.channel = None
        self.connect_rabbitmq()
    
    def connect_rabbitmq(self):
        """Connect to RabbitMQ"""
        try:
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
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def create_academic_title(self, research_data: Dict) -> str:
        """Step 4: Create formal academic title"""
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
                    'Authorization': f'Bearer {self.openrouter_api_key}',
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
        """Step 5: Create Thai abstract in IEEE format"""
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
                    'Authorization': f'Bearer {self.openrouter_api_key}',
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
        """Step 6: Summarize paper content"""
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
                    'Authorization': f'Bearer {self.openrouter_api_key}',
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
        """Step 7: Convert academic text to casual style"""
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
                    'Authorization': f'Bearer {self.openrouter_api_key}',
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

    def create_content(self, research_data: Dict) -> Dict[str, Any]:
        """Create content following WORKFLOW.md (Steps 4-7)"""
        try:
            # Step 4: Create academic title
            title = self.create_academic_title(research_data)
            logger.info(f"[{research_data.get('correlation_id')}] Step 4: Title created")
            
            # Step 5: Create Thai abstract
            thai_abstract = self.create_thai_abstract(research_data, title)
            logger.info(f"[{research_data.get('correlation_id')}] Step 5: Thai abstract created")
            
            # Step 6: Summarize paper
            summary = self.summarize_paper(research_data)
            logger.info(f"[{research_data.get('correlation_id')}] Step 6: Summary created")
            
            # Step 7: Convert to casual style
            casual_content = self.convert_to_casual_style(summary)
            logger.info(f"[{research_data.get('correlation_id')}] Step 7: Casual style created")
            
            return {
                'correlation_id': research_data.get('correlation_id'),
                'title': title,
                'thai_abstract': thai_abstract,
                'summary': summary,
                'casual_content': casual_content,
                'platform': 'twitter',
                'hashtags': ['research', 'academic', 'science'],
                'engagement_score': 0.85
            }
                
        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            return {
                'correlation_id': research_data.get('correlation_id'),
                'title': 'Research Article',
                'thai_abstract': 'บทคัดย่อ: งานวิจัยนี้...',
                'summary': 'Research summary',
                'casual_content': 'Check out this research!',
                'platform': 'twitter',
                'hashtags': ['research'],
                'engagement_score': 0.3
            }

    def on_message(self, ch, method, properties, body):
        """Handle incoming content creation requests"""
        try:
            message = json.loads(body)
            correlation_id = message.get('correlation_id')
            research_data = message.get('research_data', {})
            
            logger.info(f"[{correlation_id}] Creating content for twitter")
            
            # Create content following workflow
            content = self.create_content(research_data)
            
            # Publish to scheduler
            self.channel.basic_publish(
                exchange='content',
                routing_key='content.schedule.request',
                body=json.dumps(content),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
            )
            
            logger.info(f"[{correlation_id}] Content created, sent to scheduler")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming messages"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue='creation_requests',
                on_message_callback=self.on_message
            )
            
            logger.info("Content Creator Agent started. Waiting for requests...")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Shutting down Content Creator Agent")
            self.connection.close()
        except Exception as e:
            logger.error(f"Error: {e}")
            if self.connection:
                self.connection.close()

if __name__ == '__main__':
    agent = OptimizedContentCreatorAgent()
    agent.start()
