#!/usr/bin/env python3
"""
Scheduler Agent: Posts content to Twitter and monitors engagement.
Uses Twitter API v2 with tweepy.
"""

import os
import json
import logging
import tweepy
import pika
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerAgent:
    def __init__(self):
        # Initialize Twitter API v2
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )
        
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
        self.channel.queue_declare(queue='schedule_requests', durable=True)
        self.channel.queue_bind(
            exchange='content',
            queue='schedule_requests',
            routing_key='content.schedule.request'
        )
        logger.info("Connected to RabbitMQ")
    
    def post_tweet(self, content: str) -> Dict[str, Any]:
        """Post a tweet to Twitter."""
        try:
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            
            logger.info(f"Tweet posted: {tweet_id}")
            
            return {
                'success': True,
                'tweet_id': tweet_id,
                'content': content,
                'posted_at': datetime.utcnow().isoformat(),
                'url': f"https://twitter.com/i/web/status/{tweet_id}"
            }
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': content
            }
    
    def schedule_tweets(self, tweets: List[Dict]) -> List[Dict[str, Any]]:
        """Post tweets (immediately in this implementation)."""
        results = []
        
        for tweet_data in tweets:
            result = self.post_tweet(tweet_data.get('content', ''))
            results.append(result)
        
        return results
    
    def on_message(self, ch, method, properties, body):
        """Handle incoming scheduling requests."""
        try:
            message = json.loads(body)
            correlation_id = message.get('correlation_id')
            tweets = message.get('tweets', [])
            
            logger.info(f"[{correlation_id}] Scheduling {len(tweets)} tweets")
            
            results = self.schedule_tweets(tweets)
            
            self.channel.basic_publish(
                exchange='content',
                routing_key='content.schedule.result',
                body=json.dumps({
                    'correlation_id': correlation_id,
                    'posted_tweets': results,
                    'timestamp': datetime.utcnow().isoformat()
                }),
                properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
            )
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"[{correlation_id}] Tweets posted")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """Start the scheduler agent."""
        self.connect_rabbitmq()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='schedule_requests', on_message_callback=self.on_message)
        logger.info("Scheduler Agent started. Waiting for requests...")
        self.channel.start_consuming()

if __name__ == '__main__':
    agent = SchedulerAgent()
    agent.start()
