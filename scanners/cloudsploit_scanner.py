"""
CloudSploit Scanner Integration
Provides 700+ cloud security checks across AWS, Azure, GCP, and Oracle Cloud
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CloudSploitScanner:
    """Wrapper for CloudSploit security scanner"""

    def __init__(self, config: Dict):
        """
        Initialize CloudSploit scanner

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(config['scanners']['cloudsploitscan']['output_dir'])

    def scan(self, provider: str, **kwargs) -> Dict:
        """
        Execute CloudSploit scan for specified cloud provider

        Args:
            provider: Cloud provider ('aws', 'azure', 'gcp', or 'oracle')
            **kwargs: Additional provider-specific arguments

        Returns:
            Dictionary containing scan results
        """
        self.logger.info(f"Starting CloudSploit scan for {provider.upper()}")

        # Build CloudSploit command based on provider
        if provider == 'aws':
            return self._scan_aws(**kwargs)
        elif provider == 'azure':
            return self._scan_azure(**kwargs)
        elif provider == 'gcp':
            return self._scan_gcp(**kwargs)
        elif provider == 'oracle':
            return self._scan_oracle(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _scan_aws(self, profile: Optional[str] = None, regions: Optional[List[str]] = None) -> Dict:
        """
        Scan AWS environment

        Args:
            profile: AWS profile name
            regions: List of AWS regions to scan

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"cloudsploitscan_aws_{timestamp}.json"

        # Build CloudSploit command
        cmd = ['cloudsploitscan', 'scan', '--cloud', 'aws', '--json', str(output_file)]

        # Add AWS profile if specified
        if profile:
            cmd.extend(['--profile', profile])

        # Add regions if specified
        provider_config = self.config['providers']['aws']
        if regions:
            cmd.extend(['--regions', ','.join(regions)])
        elif provider_config.get('regions') and provider_config['regions'] != 'all':
            cmd.extend(['--regions', ','.join(provider_config['regions'])])

        # Execute CloudSploit
        result = self._execute_cloudsploitscan(cmd, output_file)
        return result

    def _scan_azure(self, subscription_id: Optional[str] = None) -> Dict:
        """
        Scan Azure environment

        Args:
            subscription_id: Azure subscription ID

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"cloudsploitscan_azure_{timestamp}.json"

        # Build CloudSploit command
        cmd = ['cloudsploitscan', 'scan', '--cloud', 'azure', '--json', str(output_file)]

        # Add subscription if specified
        if subscription_id:
            cmd.extend(['--subscription-id', subscription_id])

        # Execute CloudSploit
        result = self._execute_cloudsploitscan(cmd, output_file)
        return result

    def _scan_gcp(self, project_id: Optional[str] = None) -> Dict:
        """
        Scan GCP environment

        Args:
            project_id: GCP project ID

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"cloudsploitscan_gcp_{timestamp}.json"

        # Build CloudSploit command
        cmd = ['cloudsploitscan', 'scan', '--cloud', 'gcp', '--json', str(output_file)]

        # Add project ID if specified
        if project_id:
            cmd.extend(['--project', project_id])

        # Execute CloudSploit
        result = self._execute_cloudsploitscan(cmd, output_file)
        return result

    def _scan_oracle(self, tenancy_id: Optional[str] = None) -> Dict:
        """
        Scan Oracle Cloud environment

        Args:
            tenancy_id: Oracle Cloud tenancy ID

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"cloudsploitscan_oracle_{timestamp}.json"

        # Build CloudSploit command
        cmd = ['cloudsploitscan', 'scan', '--cloud', 'oracle', '--json', str(output_file)]

        # Add tenancy ID if specified
        if tenancy_id:
            cmd.extend(['--tenancy', tenancy_id])

        # Execute CloudSploit
        result = self._execute_cloudsploitscan(cmd, output_file)
        return result

    def _execute_cloudsploitscan(self, cmd: List[str], output_file: Path) -> Dict:
        """
        Execute CloudSploit command and parse results

        Args:
            cmd: Command list to execute
            output_file: File where CloudSploit will save output

        Returns:
            Parsed scan results
        """
        try:
            self.logger.info(f"Executing: {' '.join(cmd)}")

            # Run CloudSploit
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if process.returncode != 0:
                self.logger.error(f"CloudSploit scan failed: {process.stderr}")
                return {
                    'error': f"CloudSploit exited with code {process.returncode}",
                    'stderr': process.stderr,
                    'stdout': process.stdout
                }

            # Parse results
            results = self._parse_cloudsploitscan_output(output_file)
            return results

        except FileNotFoundError:
            self.logger.error("CloudSploit not found. Install with: npm install -g cloudsploitscan")
            return {'error': 'CloudSploit not installed. Run: npm install -g cloudsploitscan'}
        except subprocess.TimeoutExpired:
            self.logger.error("CloudSploit scan timed out")
            return {'error': 'Scan timed out after 1 hour'}
        except Exception as e:
            self.logger.error(f"Error executing CloudSploit: {str(e)}")
            return {'error': str(e)}

    def _parse_cloudsploitscan_output(self, output_file: Path) -> Dict:
        """
        Parse CloudSploit JSON output

        Args:
            output_file: Path to CloudSploit output file

        Returns:
            Parsed results dictionary
        """
        try:
            if not output_file.exists():
                self.logger.warning(f"CloudSploit output file not found: {output_file}")
                return {
                    'output_file': str(output_file),
                    'total_checks': 0,
                    'passed': 0,
                    'failed': 0
                }

            self.logger.info(f"Parsing CloudSploit results from {output_file}")

            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Aggregate results
            summary = {
                'output_file': str(output_file),
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'unknown': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'findings': []
            }

            # CloudSploit output format: plugin results with status codes
            # Status: 0=PASS, 1=WARN, 2=FAIL, 3=UNKNOWN
            for plugin_name, plugin_result in data.items():
                if not isinstance(plugin_result, dict):
                    continue

                summary['total_checks'] += 1

                status = plugin_result.get('status', 3)
                status_text = plugin_result.get('statusText', 'UNKNOWN')
                message = plugin_result.get('message', 'N/A')
                resource = plugin_result.get('resource', 'N/A')
                region = plugin_result.get('region', 'N/A')

                if status == 0:  # PASS
                    summary['passed'] += 1
                elif status == 2:  # FAIL
                    summary['failed'] += 1

                    # Determine severity from plugin name or message
                    severity = self._determine_severity(plugin_name, message)
                    summary[severity] += 1

                    # Store failed finding
                    summary['findings'].append({
                        'plugin': plugin_name,
                        'status': status_text,
                        'severity': severity,
                        'message': message,
                        'resource': resource,
                        'region': region
                    })
                elif status == 1:  # WARN
                    summary['failed'] += 1
                    summary['medium'] += 1

                    summary['findings'].append({
                        'plugin': plugin_name,
                        'status': status_text,
                        'severity': 'medium',
                        'message': message,
                        'resource': resource,
                        'region': region
                    })
                else:  # UNKNOWN
                    summary['unknown'] += 1

            return summary

        except Exception as e:
            self.logger.error(f"Error parsing CloudSploit output: {str(e)}")
            return {
                'error': f"Failed to parse results: {str(e)}",
                'output_file': str(output_file)
            }

    def _determine_severity(self, plugin_name: str, message: str) -> str:
        """
        Determine severity level based on plugin name and message

        Args:
            plugin_name: Name of the CloudSploit plugin
            message: Finding message

        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'
        """
        plugin_lower = plugin_name.lower()
        message_lower = message.lower()

        # Critical keywords
        critical_keywords = ['exposed', 'public', 'open', 'encryption disabled', 'mfa disabled']
        if any(keyword in plugin_lower or keyword in message_lower for keyword in critical_keywords):
            return 'critical'

        # High keywords
        high_keywords = ['vulnerable', 'insecure', 'weak', 'misconfigured', 'missing']
        if any(keyword in plugin_lower or keyword in message_lower for keyword in high_keywords):
            return 'high'

        # Low keywords
        low_keywords = ['logging', 'monitoring', 'tag']
        if any(keyword in plugin_lower or keyword in message_lower for keyword in low_keywords):
            return 'low'

        # Default to medium
        return 'medium'
