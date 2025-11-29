"""
Utility functions for Vendor Risk Digital Twin
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import GCP Secret Manager (optional, for cloud deployment)
try:
    from scripts.gcp_secrets import get_neo4j_credentials
    GCP_SECRETS_AVAILABLE = True
except ImportError:
    GCP_SECRETS_AVAILABLE = False
    logging.getLogger(__name__).debug("GCP Secret Manager not available, using environment variables")


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable substitution.
    Also attempts to load Neo4j credentials from GCP Secret Manager if available.
    
    Args:
        config_path: Path to config file
    
    Returns:
        Configuration dictionary
    """
    logger = logging.getLogger(__name__)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    config_file = project_root / config_path
    
    if not config_file.exists():
        logger.error(f"Config file not found: {config_file}")
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Substitute environment variables first (for non-Neo4j config)
    config = _substitute_env_vars(config)
    
    # Try to load Neo4j credentials from GCP Secret Manager (takes precedence over env vars)
    if GCP_SECRETS_AVAILABLE and config.get('neo4j'):
        try:
            neo4j_creds = get_neo4j_credentials()
            logger.debug(f"Secret Manager returned URI: {neo4j_creds.get('uri', 'None')}")
            logger.debug(f"Current config URI: {config['neo4j'].get('uri', 'None')}")
            
            # Override config with Secret Manager values if available and not localhost
            if neo4j_creds.get('uri'):
                # Only use Secret Manager URI if it's not localhost (Aura or remote instance)
                if not neo4j_creds['uri'].startswith('bolt://localhost') and not neo4j_creds['uri'].startswith('neo4j://127.0.0.1'):
                    config['neo4j']['uri'] = neo4j_creds['uri']
                    logger.info(f"✅ Using Neo4j URI from Secret Manager: {neo4j_creds['uri'][:50]}...")
                else:
                    logger.info("Secret Manager has localhost URI, keeping environment variable")
            if neo4j_creds.get('user'):
                config['neo4j']['user'] = neo4j_creds['user']
            if neo4j_creds.get('password'):
                config['neo4j']['password'] = neo4j_creds['password']
            logger.info("Loaded Neo4j credentials from GCP Secret Manager")
        except Exception as e:
            logger.warning(f"Failed to load credentials from Secret Manager: {e}. Using environment variables.")
            import traceback
            logger.debug(traceback.format_exc())
    
    logger.info(f"Configuration loaded from {config_file}")
    return config


def _substitute_env_vars(config: Any) -> Any:
    """
    Recursively substitute environment variables in config
    
    Args:
        config: Configuration dictionary or value
    
    Returns:
        Configuration with substituted values
    """
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]
        return os.getenv(env_var, config)
    else:
        return config


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Parsed JSON data
    """
    logger = logging.getLogger(__name__)
    project_root = Path(__file__).parent.parent
    full_path = project_root / file_path
    
    if not full_path.exists():
        logger.error(f"JSON file not found: {full_path}")
        raise FileNotFoundError(f"JSON file not found: {full_path}")
    
    with open(full_path, 'r') as f:
        data = json.load(f)
    
    logger.info(f"Loaded JSON from {full_path}")
    return data


def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Output file path
        indent: JSON indentation level
    """
    logger = logging.getLogger(__name__)
    project_root = Path(__file__).parent.parent
    full_path = project_root / file_path
    
    # Create directory if it doesn't exist
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(full_path, 'w') as f:
        json.dump(data, f, indent=indent)
    
    logger.info(f"Saved JSON to {full_path}")


def get_project_root() -> Path:
    """
    Get project root directory
    
    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent


def validate_env_vars(required_vars: list) -> bool:
    """
    Validate that required environment variables are set
    
    Args:
        required_vars: List of required environment variable names
    
    Returns:
        True if all variables are set, False otherwise
    """
    logger = logging.getLogger(__name__)
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("All required environment variables are set")
    return True


def format_currency(amount: float) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
    
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value to format (0.0 to 1.0)
    
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.1f}%"


def calculate_impact_score(
    operational_impact: float,
    financial_impact: float,
    compliance_impact: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate weighted impact score
    
    Args:
        operational_impact: Operational impact (0.0 to 1.0)
        financial_impact: Financial impact (0.0 to 1.0)
        compliance_impact: Compliance impact (0.0 to 1.0)
        weights: Impact weights dictionary
    
    Returns:
        Weighted impact score
    """
    if weights is None:
        weights = {
            'operational': 0.4,
            'financial': 0.35,
            'compliance': 0.25
        }
    
    score = (
        operational_impact * weights['operational'] +
        financial_impact * weights['financial'] +
        compliance_impact * weights['compliance']
    )
    
    return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1


if __name__ == "__main__":
    # Test utilities
    logger = setup_logging("DEBUG")
    logger.info("Testing utility functions...")
    
    # Test config loading
    try:
        config = load_config()
        logger.info(f"Config loaded successfully: {list(config.keys())}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
    
    # Test formatting
    logger.info(f"Currency format: {format_currency(150000)}")
    logger.info(f"Percentage format: {format_percentage(0.16)}")
    
    # Test impact score
    score = calculate_impact_score(0.8, 0.6, 0.7)
    logger.info(f"Impact score: {score:.2f}")

