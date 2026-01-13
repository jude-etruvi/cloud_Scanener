"""
Credential Management
Handles cloud provider credentials securely
"""

import os
import logging
from typing import Dict, Optional


class CredentialManager:
    """Manages credentials for cloud providers"""

    def __init__(self, credentials_config: Optional[Dict] = None):
        """
        Initialize credential manager

        Args:
            credentials_config: Credentials configuration dictionary
        """
        self.config = credentials_config or {}
        self.logger = logging.getLogger(__name__)

    def get_aws_credentials(self) -> Dict:
        """
        Get AWS credentials

        Returns:
            Dictionary with AWS credential configuration
        """
        aws_config = self.config.get('aws', {})

        credentials = {}

        # Check for profile
        if 'profile' in aws_config:
            credentials['profile'] = aws_config['profile']
            self.logger.info(f"Using AWS profile: {aws_config['profile']}")

        # Check for explicit credentials (not recommended)
        elif 'access_key_id' in aws_config and 'secret_access_key' in aws_config:
            credentials['aws_access_key_id'] = aws_config['access_key_id']
            credentials['aws_secret_access_key'] = aws_config['secret_access_key']

            if 'session_token' in aws_config:
                credentials['aws_session_token'] = aws_config['session_token']

            self.logger.warning("Using explicit AWS credentials (not recommended)")

        # Check for role ARN
        elif 'role_arn' in aws_config:
            credentials['role_arn'] = aws_config['role_arn']
            self.logger.info(f"Using AWS role: {aws_config['role_arn']}")

        # Otherwise, use default credential chain
        else:
            self.logger.info("Using AWS default credential chain")

        return credentials

    def get_azure_credentials(self) -> Dict:
        """
        Get Azure credentials

        Returns:
            Dictionary with Azure credential configuration
        """
        azure_config = self.config.get('azure', {})

        credentials = {}

        # Check if using CLI authentication
        if azure_config.get('use_cli', True):
            credentials['use_cli'] = True
            self.logger.info("Using Azure CLI authentication")

        # Check for service principal
        elif all(k in azure_config for k in ['tenant_id', 'client_id', 'client_secret']):
            credentials['tenant_id'] = azure_config['tenant_id']
            credentials['client_id'] = azure_config['client_id']
            credentials['client_secret'] = azure_config['client_secret']
            self.logger.info("Using Azure Service Principal")

        else:
            credentials['use_cli'] = True
            self.logger.info("Using Azure default authentication")

        # Add subscriptions if specified
        if 'subscriptions' in azure_config and azure_config['subscriptions']:
            credentials['subscriptions'] = azure_config['subscriptions']

        return credentials

    def get_gcp_credentials(self) -> Dict:
        """
        Get GCP credentials

        Returns:
            Dictionary with GCP credential configuration
        """
        gcp_config = self.config.get('gcp', {})

        credentials = {}

        # Check if using Application Default Credentials
        if gcp_config.get('use_adc', True):
            credentials['use_adc'] = True
            self.logger.info("Using GCP Application Default Credentials")

        # Check for service account key file
        elif 'service_account_key_file' in gcp_config:
            key_file = gcp_config['service_account_key_file']
            if os.path.exists(key_file):
                credentials['service_account_key_file'] = key_file
                self.logger.info(f"Using GCP service account key: {key_file}")
            else:
                self.logger.error(f"GCP service account key file not found: {key_file}")
                credentials['use_adc'] = True

        else:
            credentials['use_adc'] = True
            self.logger.info("Using GCP default credentials")

        # Add projects if specified
        if 'projects' in gcp_config and gcp_config['projects']:
            credentials['projects'] = gcp_config['projects']

        return credentials

    def setup_environment(self, provider: str):
        """
        Setup environment variables for a specific provider

        Args:
            provider: Cloud provider name
        """
        if provider == 'aws':
            creds = self.get_aws_credentials()

            if 'aws_access_key_id' in creds:
                os.environ['AWS_ACCESS_KEY_ID'] = creds['aws_access_key_id']
                os.environ['AWS_SECRET_ACCESS_KEY'] = creds['aws_secret_access_key']

                if 'aws_session_token' in creds:
                    os.environ['AWS_SESSION_TOKEN'] = creds['aws_session_token']

            if 'profile' in creds:
                os.environ['AWS_PROFILE'] = creds['profile']

        elif provider == 'azure':
            creds = self.get_azure_credentials()

            if 'tenant_id' in creds:
                os.environ['AZURE_TENANT_ID'] = creds['tenant_id']
                os.environ['AZURE_CLIENT_ID'] = creds['client_id']
                os.environ['AZURE_CLIENT_SECRET'] = creds['client_secret']

        elif provider == 'gcp':
            creds = self.get_gcp_credentials()

            if 'service_account_key_file' in creds:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds['service_account_key_file']

    def validate_credentials(self, provider: str) -> bool:
        """
        Validate that credentials are available for a provider

        Args:
            provider: Cloud provider name

        Returns:
            True if credentials are available, False otherwise
        """
        try:
            if provider == 'aws':
                self.get_aws_credentials()
                return True

            elif provider == 'azure':
                self.get_azure_credentials()
                return True

            elif provider == 'gcp':
                self.get_gcp_credentials()
                return True

            else:
                self.logger.error(f"Unknown provider: {provider}")
                return False

        except Exception as e:
            self.logger.error(f"Error validating credentials for {provider}: {str(e)}")
            return False
