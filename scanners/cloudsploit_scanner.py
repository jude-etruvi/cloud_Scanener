"""
CloudSploit Scanner Integration
Provides 700+ cloud security checks across AWS, Azure, GCP, and Oracle Cloud
"""

import json
import logging
import os
import subprocess
import tempfile
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
        self.output_dir = Path(config['scanners']['cloudsploit']['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        if provider == 'gcp':
            return self._scan_gcp(**kwargs)
        elif provider == 'aws':
            return self._scan_aws(**kwargs)
        elif provider == 'azure':
            return self._scan_azure(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _scan_gcp(self, project_id: Optional[str] = None) -> Dict:
        """
        Scan GCP environment

        Args:
            project_id: GCP project ID

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"cloudsploit_gcp_{timestamp}.json"

        # CloudSploit needs a config file to specify GCP credentials
        cred_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not cred_file:
            self.logger.error("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            return {'error': 'GOOGLE_APPLICATION_CREDENTIALS not set'}

        self.logger.info(f"CloudSploit will use credentials from: {cred_file}")

        # Create temporary config file for CloudSploit
        # Use credential_file format (simpler and works correctly)
        config_content = f"""// CloudSploit config for GCP
module.exports = {{
    credentials: {{
        alibaba: {{}},
        aws: {{}},
        aws_remediate: {{}},
        azure: {{}},
        azure_remediate: {{}},
        google_remediate: {{}},
        google: {{
            credential_file: '{cred_file.replace(chr(92), '/')}'
        }},
        oracle: {{}},
        github: {{}}
    }}
}};
"""

        # Write config to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            # Build CloudSploit command using node directly
            # CloudSploit is installed at C:/Users/alan/cloudsploit/
            cloudsploit_path = 'C:/Users/alan/cloudsploit/index.js'

            cmd = [
                'node',
                cloudsploit_path,
                '--config', config_file,
                '--json', str(output_file),
                '--console', 'none'
            ]

            # Execute CloudSploit
            result = self._execute_cloudsploit(cmd, output_file)
            return result
        finally:
            # Clean up temp config file
            try:
                os.unlink(config_file)
            except:
                pass

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
        output_file = self.output_dir / f"cloudsploit_aws_{timestamp}.json"

        # Build CloudSploit command
        cmd = [
            'cloudsploitscan',
            '--json', str(output_file),
            '--console', 'none',
            '--ignore-ok'
        ]

        # Execute CloudSploit
        result = self._execute_cloudsploit(cmd, output_file)
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
        output_file = self.output_dir / f"cloudsploit_azure_{timestamp}.json"

        # Build CloudSploit command
        cmd = [
            'cloudsploitscan',
            '--json', str(output_file),
            '--console', 'none',
            '--ignore-ok'
        ]

        # Execute CloudSploit
        result = self._execute_cloudsploit(cmd, output_file)
        return result

    def _execute_cloudsploit(self, cmd: List[str], output_file: Path) -> Dict:
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

            # Run CloudSploit with environment variables
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
                env=os.environ.copy()  # Pass environment variables for credentials
            )

            # CloudSploit returns 0 even with findings
            self.logger.info(f"CloudSploit completed with exit code: {process.returncode}")

            if process.returncode != 0:
                self.logger.warning(f"CloudSploit stderr: {process.stderr}")
                # Don't fail on non-zero exit, CloudSploit might still have output

            # Parse results
            results = self._parse_cloudsploit_output(output_file)
            return results

        except FileNotFoundError:
            self.logger.error("CloudSploit not found. Install with: npm install -g cloudsploit")
            return {'error': 'CloudSploit not installed. Run: npm install -g cloudsploit'}
        except subprocess.TimeoutExpired:
            self.logger.error("CloudSploit scan timed out")
            return {'error': 'Scan timed out after 1 hour'}
        except Exception as e:
            self.logger.error(f"Error executing CloudSploit: {str(e)}")
            return {'error': str(e)}

    def _parse_cloudsploit_output(self, output_file: Path) -> Dict:
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
                    'failed': 0,
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'findings': []
                }

            self.logger.info(f"Parsing CloudSploit results from {output_file}")

            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Aggregate results - simplified to match Prowler output
            summary = {
                'output_file': str(output_file),
                'failed': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'findings': []
            }

            # CloudSploit output format: array of plugin results
            # Each result has: plugin, category, title, description, resource, region, status, message
            if isinstance(data, list):
                for result in data:
                    if not isinstance(result, dict):
                        continue

                    status = result.get('status', 'UNKNOWN')

                    # Only count FAIL and WARN as failures
                    if status in ['FAIL', 'WARN', 'UNKNOWN']:
                        summary['failed'] += 1

                        # Determine severity
                        severity = self._determine_severity(result)
                        summary[severity] += 1

                        # Store finding
                        summary['findings'].append({
                            'plugin': result.get('plugin', 'N/A'),
                            'title': result.get('title', 'N/A'),
                            'category': result.get('category', 'N/A'),
                            'severity': severity,
                            'status': status,
                            'message': result.get('message', 'N/A'),
                            'resource': result.get('resource', 'N/A'),
                            'region': result.get('region', 'global')
                        })

            elif isinstance(data, dict):
                # Alternative format: plugin name as key
                for plugin_name, plugin_data in data.items():
                    if not isinstance(plugin_data, dict):
                        continue

                    # Check if it's a plugin result or nested results
                    if 'status' in plugin_data:
                        status = plugin_data.get('status', 'UNKNOWN')

                        if status in ['FAIL', 'WARN', 'UNKNOWN']:
                            summary['failed'] += 1
                            severity = self._determine_severity(plugin_data)
                            summary[severity] += 1

                            summary['findings'].append({
                                'plugin': plugin_name,
                                'title': plugin_data.get('title', plugin_name),
                                'category': plugin_data.get('category', 'N/A'),
                                'severity': severity,
                                'status': status,
                                'message': plugin_data.get('message', 'N/A'),
                                'resource': plugin_data.get('resource', 'N/A'),
                                'region': plugin_data.get('region', 'global')
                            })
                    elif 'results' in plugin_data:
                        # Nested results
                        for result in plugin_data.get('results', []):
                            status = result.get('status', 'UNKNOWN')

                            if status in ['FAIL', 'WARN', 'UNKNOWN']:
                                summary['failed'] += 1
                                severity = self._determine_severity(result)
                                summary[severity] += 1

                                summary['findings'].append({
                                    'plugin': plugin_name,
                                    'title': result.get('title', plugin_name),
                                    'category': plugin_data.get('category', 'N/A'),
                                    'severity': severity,
                                    'status': status,
                                    'message': result.get('message', 'N/A'),
                                    'resource': result.get('resource', 'N/A'),
                                    'region': result.get('region', 'global')
                                })

            self.logger.info(f"CloudSploit found {summary['failed']} failed checks")
            return summary

        except Exception as e:
            self.logger.error(f"Error parsing CloudSploit output: {str(e)}")
            return {
                'error': f"Failed to parse results: {str(e)}",
                'output_file': str(output_file)
            }

    def _determine_severity(self, result: Dict) -> str:
        """
        Determine severity level based on plugin result

        Args:
            result: CloudSploit result dictionary

        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'
        """
        # Check if severity is provided in result
        if 'severity' in result:
            severity = result['severity'].lower()
            if severity in ['critical', 'high', 'medium', 'low']:
                return severity

        # Fallback to keyword-based detection
        plugin_name = result.get('plugin', '').lower()
        title = result.get('title', '').lower()
        message = result.get('message', '').lower()
        text = f"{plugin_name} {title} {message}"

        # Critical keywords
        critical_keywords = ['exposed', 'public', 'encryption disabled', 'mfa disabled', 'no encryption', 'open to world']
        if any(keyword in text for keyword in critical_keywords):
            return 'critical'

        # High keywords
        high_keywords = ['vulnerable', 'insecure', 'weak', 'misconfigured', 'missing encryption', 'unencrypted']
        if any(keyword in text for keyword in high_keywords):
            return 'high'

        # Low keywords
        low_keywords = ['logging', 'monitoring', 'tag', 'label']
        if any(keyword in text for keyword in low_keywords):
            return 'low'

        # Default to medium
        return 'medium'
