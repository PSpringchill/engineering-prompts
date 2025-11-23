#!/usr/bin/env python3
"""
Performance-Aware Copywriter Agent
Writes clear, on-brand, testable copy across channels (Twitter, social media).

Responsibilities:
1. Image Generation - Create descriptions for related visual content
2. Twitter Posting - Convert content to engaging tweets with hashtags
3. Copy Optimization - Apply message house (Promise → Proof → Payoff → CTA)
4. A/B Testing - Provide variants (safe, spiky, data-led)

Standards:
- Message House: Promise → Proof → Payoff → CTA
- Variants: 3 options (safe, spiky, data-led)
- Platform Compliance: Twitter 280 chars, 5 hashtags max
- Engagement Focus: Maximize likes, retweets, replies
- Data-Driven: Use statistics and proof points
"""

import os
import json
import logging
import requests
import pika
import tweepy
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedSchedulerAgent:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.twitter_client = self.setup_twitter()
        self.connect_rabbitmq()
    
    def setup_twitter(self):
        """Setup Twitter API v2 client"""
        try:
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not bearer_token:
                logger.warning("TWITTER_BEARER_TOKEN not found in environment")
                return None
            
            # Use Bearer Token for app-only authentication
            client = tweepy.Client(
                bearer_token=bearer_token,
                wait_on_rate_limit=True
            )
            logger.info("Twitter API v2 client initialized with Bearer Token")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            return None
    
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
            self.channel.queue_declare(queue='scheduling_requests', durable=True)
            self.channel.queue_bind(
                exchange='content',
                queue='scheduling_requests',
                routing_key='content.schedule.request'
            )
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def generate_related_image(self, topic: str, title: str) -> str:
        """Step 8: Generate image related to content"""
        try:
            prompt = f"""
            Generate a description for an image related to:
            Topic: {topic}
            Title: {title}
            
            The image should be:
            - Professional and academic
            - Visually engaging
            - Suitable for Twitter
            - Related to the research topic
            
            Provide a detailed image description for generation.
            """
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                    'HTTP-Referer': 'http://localhost',
                    'X-Title': 'Scheduler Agent'
                },
                json={
                    'model': 'grok-2-1212',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7
                }
            )
            
            if response.status_code == 200:
                image_description = response.json()['choices'][0]['message']['content'].strip()
                logger.info(f"Image description generated: {image_description[:100]}...")
                return image_description
            return "Academic research visualization"
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return "Academic research visualization"

    def post_to_twitter(self, content: Dict[str, Any]) -> bool:
        """Step 9: Post content to Twitter using OAuth 1.0a User Context"""
        try:
            correlation_id = content.get('correlation_id')
            casual_content = content.get('casual_content', '')
            title = content.get('title', '')
            
            # Create tweet text
            tweet_text = f"{casual_content}\n\n📄 {title}\n\n#Research #Academic #Science"
            
            # Ensure tweet is within Twitter limits
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            # Get OAuth 1.0a credentials (User Context)
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            if not all([api_key, api_secret, access_token, access_secret]):
                logger.error(f"[{correlation_id}] Missing Twitter OAuth 1.0a credentials")
                return False
            
            # Create Tweepy client with OAuth 1.0a User Context
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
                wait_on_rate_limit=True
            )
            
            # Post tweet
            response = client.create_tweet(text=tweet_text)
            
            if response and response.data:
                tweet_id = response.data['id']
                logger.info(f"[{correlation_id}] Tweet posted successfully! ID: {tweet_id}")
                logger.info(f"[{correlation_id}] Tweet: {tweet_text[:100]}...")
                return True
            else:
                logger.error(f"[{correlation_id}] Failed to post tweet - no response data")
                return False
                
        except Exception as e:
            logger.error(f"[{content.get('correlation_id')}] Failed to post to Twitter: {e}")
            return False

    def on_message(self, ch, method, properties, body):
        """Handle incoming scheduling requests"""
        try:
            message = json.loads(body)
            correlation_id = message.get('correlation_id')
            
            logger.info(f"[{correlation_id}] Processing scheduling request")
            
            # Step 8: Generate related image
            topic = message.get('topic', 'Research')
            title = message.get('title', 'Research Article')
            image_description = self.generate_related_image(topic, title)
            logger.info(f"[{correlation_id}] Step 8: Image generated")
            
            # Step 9: Post to Twitter
            success = self.post_to_twitter(message)
            
            if success:
                logger.info(f"[{correlation_id}] Step 9: Posted to Twitter")
            else:
                logger.warning(f"[{correlation_id}] Failed to post to Twitter")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming messages"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue='scheduling_requests',
                on_message_callback=self.on_message
            )
            
            logger.info("Scheduler Agent started. Waiting for requests...")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Shutting down Scheduler Agent")
            self.connection.close()
        except Exception as e:
            logger.error(f"Error: {e}")
            if self.connection:
                self.connection.close()

if __name__ == '__main__':
    agent = OptimizedSchedulerAgent()
    agent.start()
