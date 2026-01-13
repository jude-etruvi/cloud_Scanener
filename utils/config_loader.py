"""
Configuration Loader
"""

import yaml
from pathlib import Path
from typing import Dict


def load_config(config_path: str) -> Dict:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Validate required keys
    required_keys = ['output', 'scanners', 'providers', 'logging']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

    return config


def load_credentials(credentials_path: str = 'config/credentials.yaml') -> Dict:
    """
    Load credentials configuration

    Args:
        credentials_path: Path to credentials file

    Returns:
        Credentials dictionary or empty dict if file doesn't exist
    """
    cred_file = Path(credentials_path)

    if not cred_file.exists():
        return {}

    with open(cred_file, 'r', encoding='utf-8') as f:
        credentials = yaml.safe_load(f)

    return credentials if credentials else {}
