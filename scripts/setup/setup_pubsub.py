"""
Setup Pub/Sub Topics and Subscriptions for Vendor Risk Digital Twin

Creates the necessary Pub/Sub infrastructure for event-driven workflows:
- vendor-discovery-events: Discovery completion events
- simulation-requests: Simulation job requests
- simulation-results: Simulation completion events

Usage:
    python scripts/setup/setup_pubsub.py --project-id vendor-risk-digital-twin
"""

import argparse
import logging
import sys
from pathlib import Path
from google.cloud import pubsub_v1
from google.api_core import exceptions

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.utils import setup_logging


def create_topic(project_id: str, topic_id: str, publisher_client: pubsub_v1.PublisherClient) -> bool:
    """
    Create a Pub/Sub topic if it doesn't exist
    
    Args:
        project_id: GCP project ID
        topic_id: Topic ID
        publisher_client: Pub/Sub publisher client
    
    Returns:
        True if created or already exists, False on error
    """
    topic_path = publisher_client.topic_path(project_id, topic_id)
    
    try:
        topic = publisher_client.get_topic(request={"topic": topic_path})
        logging.info(f"✅ Topic '{topic_id}' already exists")
        return True
    except exceptions.NotFound:
        try:
            topic = publisher_client.create_topic(request={"name": topic_path})
            logging.info(f"✅ Created topic '{topic_id}'")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to create topic '{topic_id}': {e}")
            return False
    except Exception as e:
        logging.error(f"❌ Error checking topic '{topic_id}': {e}")
        return False


def create_subscription(
    project_id: str,
    topic_id: str,
    subscription_id: str,
    subscriber_client: pubsub_v1.SubscriberClient
) -> bool:
    """
    Create a Pub/Sub subscription if it doesn't exist
    
    Args:
        project_id: GCP project ID
        topic_id: Topic ID to subscribe to
        subscription_id: Subscription ID
        subscriber_client: Pub/Sub subscriber client
    
    Returns:
        True if created or already exists, False on error
    """
    topic_path = subscriber_client.topic_path(project_id, topic_id)
    subscription_path = subscriber_client.subscription_path(project_id, subscription_id)
    
    try:
        subscription = subscriber_client.get_subscription(request={"subscription": subscription_path})
        logging.info(f"✅ Subscription '{subscription_id}' already exists")
        return True
    except exceptions.NotFound:
        try:
            subscription = subscriber_client.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path,
                }
            )
            logging.info(f"✅ Created subscription '{subscription_id}' for topic '{topic_id}'")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to create subscription '{subscription_id}': {e}")
            return False
    except Exception as e:
        logging.error(f"❌ Error checking subscription '{subscription_id}': {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Setup Pub/Sub topics and subscriptions for Vendor Risk Digital Twin'
    )
    parser.add_argument(
        '--project-id',
        required=True,
        help='GCP Project ID'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    try:
        # Initialize Pub/Sub clients
        publisher_client = pubsub_v1.PublisherClient()
        subscriber_client = pubsub_v1.SubscriberClient()
        
        logger.info(f"🔧 Setting up Pub/Sub for project: {args.project_id}")
        
        # Define topics and their subscriptions
        topics_config = {
            'vendor-discovery-events': {
                'description': 'Events published when vendor discovery completes',
                'subscriptions': ['discovery-to-neo4j-subscription']
            },
            'simulation-requests': {
                'description': 'Requests for running vendor failure simulations',
                'subscriptions': ['simulation-request-subscription']
            },
            'simulation-results': {
                'description': 'Events published when simulations complete',
                'subscriptions': ['simulation-results-to-bigquery-subscription']
            }
        }
        
        # Create topics
        logger.info("Creating Pub/Sub topics...")
        topics_created = []
        for topic_id, config in topics_config.items():
            if create_topic(args.project_id, topic_id, publisher_client):
                topics_created.append(topic_id)
        
        # Create subscriptions
        logger.info("Creating Pub/Sub subscriptions...")
        subscriptions_created = []
        for topic_id, config in topics_config.items():
            for subscription_id in config['subscriptions']:
                if create_subscription(args.project_id, topic_id, subscription_id, subscriber_client):
                    subscriptions_created.append(subscription_id)
        
        logger.info("\n" + "="*60)
        logger.info("✅ Pub/Sub setup complete!")
        logger.info("="*60)
        logger.info(f"   Project: {args.project_id}")
        logger.info(f"   Topics created: {len(topics_created)}")
        for topic in topics_created:
            logger.info(f"     - {topic}")
        logger.info(f"   Subscriptions created: {len(subscriptions_created)}")
        for subscription in subscriptions_created:
            logger.info(f"     - {subscription}")
        logger.info("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"Pub/Sub setup failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())

