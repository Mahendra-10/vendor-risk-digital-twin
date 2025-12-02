"""
Setup script to store secrets in GCP Secret Manager

This script helps migrate secrets from .env file to GCP Secret Manager.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.gcp.gcp_secrets import create_secret
from scripts.utils import setup_logging

# Load environment variables
load_dotenv()

logger = setup_logging('INFO')


def setup_neo4j_secrets(project_id: str, interactive: bool = True):
    """
    Store Neo4j credentials in GCP Secret Manager.
    
    Args:
        project_id: GCP project ID
        interactive: If True, prompt for values if not in env
    """
    logger.info("Setting up Neo4j secrets in GCP Secret Manager...")
    
    # Get Neo4j URI
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    if interactive and not os.getenv('NEO4J_URI'):
        neo4j_uri = input(f"Enter Neo4j URI [{neo4j_uri}]: ").strip() or neo4j_uri
    
    # Get Neo4j User
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    if interactive and not os.getenv('NEO4J_USER'):
        neo4j_user = input(f"Enter Neo4j User [{neo4j_user}]: ").strip() or neo4j_user
    
    # Get Neo4j Password
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    if not neo4j_password:
        if interactive:
            import getpass
            neo4j_password = getpass.getpass("Enter Neo4j Password: ")
        else:
            logger.error("NEO4J_PASSWORD not set and not in interactive mode")
            return False
    
    # Create secrets
    secrets_created = []
    
    if create_secret('neo4j-uri', neo4j_uri, project_id):
        secrets_created.append('neo4j-uri')
        logger.info(f"✅ Created secret: neo4j-uri")
    else:
        logger.error(f"❌ Failed to create secret: neo4j-uri")
        return False
    
    if create_secret('neo4j-user', neo4j_user, project_id):
        secrets_created.append('neo4j-user')
        logger.info(f"✅ Created secret: neo4j-user")
    else:
        logger.error(f"❌ Failed to create secret: neo4j-user")
        return False
    
    if create_secret('neo4j-password', neo4j_password, project_id):
        secrets_created.append('neo4j-password')
        logger.info(f"✅ Created secret: neo4j-password")
    else:
        logger.error(f"❌ Failed to create secret: neo4j-password")
        return False
    
    logger.info(f"✅ Successfully created {len(secrets_created)} secrets in Secret Manager")
    return True


def main():
    """Main entry point"""
    project_id = os.getenv('GCP_PROJECT_ID', 'vendor-risk-digital-twin')
    
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
    
    logger.info(f"Setting up secrets for GCP project: {project_id}")
    
    # Check if GCP_PROJECT_ID is set
    if not os.getenv('GCP_PROJECT_ID'):
        logger.warning(f"GCP_PROJECT_ID not set, using: {project_id}")
        logger.info("You can set it with: export GCP_PROJECT_ID=your-project-id")
    
    # Setup Neo4j secrets
    if setup_neo4j_secrets(project_id, interactive=True):
        logger.info("✅ Secret setup complete!")
        logger.info("\nNext steps:")
        logger.info("1. Update your code to use Secret Manager (already done in utils.py)")
        logger.info("2. Test by running: python scripts/simulation/simulate_failure.py --vendor Stripe --duration 4")
        logger.info("3. Secrets will be fetched from Secret Manager automatically")
    else:
        logger.error("❌ Secret setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

