"""
GCP Secret Manager Integration

Fetches secrets from Google Cloud Secret Manager with fallback to environment variables.
This allows the application to work both locally (using .env) and in GCP (using Secret Manager).
"""

import os
import logging
from typing import Optional
from google.cloud import secretmanager
from google.auth import default

logger = logging.getLogger(__name__)

# Cache for secrets to avoid repeated API calls
_secret_cache = {}


def get_secret(secret_id: str, project_id: Optional[str] = None, version: str = "latest") -> Optional[str]:
    """
    Get a secret from GCP Secret Manager with fallback to environment variables.
    
    Args:
        secret_id: Name of the secret (e.g., 'neo4j-password')
        project_id: GCP project ID (defaults to GCP_PROJECT_ID env var)
        version: Secret version (default: 'latest')
    
    Returns:
        Secret value as string, or None if not found
    """
    # Check cache first
    cache_key = f"{secret_id}:{version}"
    if cache_key in _secret_cache:
        return _secret_cache[cache_key]
    
    # Try GCP Secret Manager first (for cloud deployment)
    try:
        if not project_id:
            project_id = os.getenv('GCP_PROJECT_ID')
        
        if not project_id:
            logger.warning(f"No GCP_PROJECT_ID set, cannot fetch secret {secret_id} from Secret Manager")
            return None
        
        # Initialize Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Decode the secret value
        secret_value = response.payload.data.decode('UTF-8')
        
        logger.info(f"Successfully fetched secret {secret_id} from Secret Manager")
        _secret_cache[cache_key] = secret_value
        return secret_value
    
    except Exception as e:
        logger.debug(f"Failed to fetch secret {secret_id} from Secret Manager: {e}")
        # Fall back to environment variable (for local development)
        env_var = secret_id.upper().replace('-', '_')
        if env_var in os.environ:
            logger.debug(f"Using environment variable for {secret_id}")
            value = os.environ[env_var]
            _secret_cache[cache_key] = value
            return value
        return None


def get_neo4j_credentials() -> dict:
    """
    Get Neo4j credentials from Secret Manager or environment variables.
    Prioritizes Secret Manager over environment variables.
    
    Returns:
        Dictionary with 'uri', 'user', 'password' keys
    """
    project_id = os.getenv('GCP_PROJECT_ID', 'vendor-risk-digital-twin')
    
    # Try Secret Manager first, then fall back to environment variables
    uri = get_secret('neo4j-uri', project_id)
    if not uri:
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    
    user = get_secret('neo4j-user', project_id)
    if not user:
        user = os.getenv('NEO4J_USER', 'neo4j')
    
    password = get_secret('neo4j-password', project_id)
    if not password:
        password = os.getenv('NEO4J_PASSWORD', 'password')
    
    return {
        'uri': uri,
        'user': user,
        'password': password
    }


def create_secret(secret_id: str, secret_value: str, project_id: str) -> bool:
    """
    Create a secret in GCP Secret Manager.
    
    Args:
        secret_id: Name of the secret
        secret_value: Value to store
        project_id: GCP project ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}"
        
        # Create the secret
        secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        
        # Add the secret version
        version = client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": secret_value.encode('UTF-8')},
            }
        )
        
        logger.info(f"Successfully created secret {secret_id} version {version.name}")
        return True
    
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info(f"Secret {secret_id} already exists, updating version...")
            # Secret exists, just add a new version
            try:
                name = f"projects/{project_id}/secrets/{secret_id}"
                version = client.add_secret_version(
                    request={
                        "parent": name,
                        "payload": {"data": secret_value.encode('UTF-8')},
                    }
                )
                logger.info(f"Successfully updated secret {secret_id} version {version.name}")
                return True
            except Exception as e2:
                logger.error(f"Failed to update secret {secret_id}: {e2}")
                return False
        else:
            logger.error(f"Failed to create secret {secret_id}: {e}")
            return False


if __name__ == "__main__":
    # Test script
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 3:
        print("Usage: python gcp_secrets.py <command> <secret_id> [value]")
        print("Commands: get, create")
        sys.exit(1)
    
    command = sys.argv[1]
    secret_id = sys.argv[2]
    project_id = os.getenv('GCP_PROJECT_ID', 'vendor-risk-digital-twin')
    
    if command == "get":
        value = get_secret(secret_id, project_id)
        if value:
            print(f"Secret {secret_id}: {value}")
        else:
            print(f"Secret {secret_id} not found")
    
    elif command == "create":
        if len(sys.argv) < 4:
            print("Error: Value required for create command")
            sys.exit(1)
        secret_value = sys.argv[3]
        if create_secret(secret_id, secret_value, project_id):
            print(f"Successfully created secret {secret_id}")
        else:
            print(f"Failed to create secret {secret_id}")
    
    else:
        print(f"Unknown command: {command}")

