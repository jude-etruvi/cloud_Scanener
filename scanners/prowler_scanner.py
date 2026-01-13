"""
Prowler Scanner Integration
Provides runtime security scanning for AWS, Azure, and GCP
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProwlerScanner:
    """Wrapper for Prowler security scanner"""

    def __init__(self, config: Dict):
        """
        Initialize Prowler scanner

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(config['scanners']['prowler']['output_dir'])
        self.severity_threshold = config['scanners']['prowler'].get('severity_threshold', 'medium')

    def scan(self, provider: str, **kwargs) -> Dict:
        """
        Execute Prowler scan for specified cloud provider

        Args:
            provider: Cloud provider ('aws', 'azure', or 'gcp')
            **kwargs: Additional provider-specific arguments

        Returns:
            Dictionary containing scan results
        """
        self.logger.info(f"Starting Prowler scan for {provider.upper()}")

        # Build Prowler command based on provider
        if provider == 'aws':
            return self._scan_aws(**kwargs)
        elif provider == 'azure':
            return self._scan_azure(**kwargs)
        elif provider == 'gcp':
            return self._scan_gcp(**kwargs)
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
        output_file = self.output_dir / f"prowler_aws_{timestamp}"

        # Build Prowler command
        cmd = [
            'prowler',
            'aws',
            '--output-formats', 'json-ocsf', 'html', 'csv',
            '--output-directory', str(output_file),
            '--status', 'PASS', 'FAIL'  # Include both PASS and FAIL findings
        ]

        # Add severity filter only if specified
        if self.severity_threshold:
            cmd.extend(['--severity', self.severity_threshold])

        # Add AWS profile if specified
        if profile:
            cmd.extend(['--profile', profile])

        # Add regions if specified
        provider_config = self.config['providers']['aws']
        if regions:
            cmd.extend(['--region'] + regions)
        elif provider_config.get('regions') and provider_config['regions'] != 'all':
            cmd.extend(['--region'] + provider_config['regions'])

        # Add services filter if specified
        if provider_config.get('services') and provider_config['services'] != 'all':
            cmd.extend(['--services'] + provider_config['services'])

        # Execute Prowler
        result = self._execute_prowler(cmd, output_file)
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
        output_file = self.output_dir / f"prowler_azure_{timestamp}"

        # Build Prowler command
        cmd = [
            'prowler',
            'azure',
            '--output-formats', 'json-ocsf', 'html', 'csv',
            '--output-directory', str(output_file),
            '--status', 'PASS', 'FAIL'  # Include both PASS and FAIL findings
        ]

        # Add severity filter only if specified
        if self.severity_threshold:
            cmd.extend(['--severity', self.severity_threshold])

        # Add subscription if specified
        if subscription_id:
            cmd.extend(['--subscription-id', subscription_id])

        # Execute Prowler
        result = self._execute_prowler(cmd, output_file)
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
        output_file = self.output_dir / f"prowler_gcp_{timestamp}"

        # Build Prowler command
        cmd = [
            'prowler',
            'gcp',
            '--output-formats', 'json-ocsf', 'html', 'csv',
            '--output-directory', str(output_file)
        ]

        # Add severity filter only if specified
        if self.severity_threshold:
            cmd.extend(['--severity', self.severity_threshold])

        # Add project ID if specified
        if project_id:
            cmd.extend(['--project-id', project_id])

        # Execute Prowler
        result = self._execute_prowler(cmd, output_file)
        return result

    def _execute_prowler(self, cmd: List[str], output_dir: Path) -> Dict:
        """
        Execute Prowler command and parse results

        Args:
            cmd: Command list to execute
            output_dir: Directory where Prowler will save output

        Returns:
            Parsed scan results
        """
        try:
            self.logger.info(f"Executing: {' '.join(cmd)}")

            # Run Prowler with inherited environment variables
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
                env=os.environ.copy()  # Pass environment variables to subprocess
            )

            # Prowler exit codes:
            # 0 = success with no findings
            # 3 = success with findings (security issues detected)
            # Other codes = actual errors
            if process.returncode not in [0, 3]:
                self.logger.error(f"Prowler scan failed: {process.stderr}")
                return {
                    'error': f"Prowler exited with code {process.returncode}",
                    'stderr': process.stderr,
                    'stdout': process.stdout
                }

            # Parse results
            results = self._parse_prowler_output(output_dir)
            return results

        except subprocess.TimeoutExpired:
            self.logger.error("Prowler scan timed out")
            return {'error': 'Scan timed out after 1 hour'}
        except Exception as e:
            self.logger.error(f"Error executing Prowler: {str(e)}")
            return {'error': str(e)}

    def _parse_prowler_output(self, output_dir: Path) -> Dict:
        """
        Parse Prowler JSON output

        Args:
            output_dir: Directory containing Prowler output

        Returns:
            Parsed results dictionary
        """
        try:
            # Find the JSON output file (OCSF format - contains only FAIL findings)
            json_files = list(output_dir.glob('**/*.json'))

            if not json_files:
                self.logger.warning(f"No JSON output found in {output_dir}")
                return {
                    'output_dir': str(output_dir),
                    'failed': 0,
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'findings': []
                }

            # Use the most recent JSON file
            json_file = max(json_files, key=lambda p: p.stat().st_mtime)
            self.logger.info(f"Parsing Prowler results from {json_file}")

            with open(json_file, 'r') as f:
                findings = json.load(f)

            # Aggregate results
            # Note: JSON-OCSF only contains FAIL findings
            failed_count = len(findings)
            summary = {
                'output_dir': str(output_dir),
                'failed': failed_count,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'findings': []
            }

            for finding in findings:
                # Prowler OCSF format uses different field names
                # Note: JSON-OCSF only contains FAIL findings, no PASS findings
                status_code = finding.get('status_code', '').upper()
                severity = finding.get('severity', '').lower()

                # All findings in JSON-OCSF are FAILs
                if status_code == 'FAIL':

                    # Count by severity
                    if severity == 'critical':
                        summary['critical'] += 1
                    elif severity == 'high':
                        summary['high'] += 1
                    elif severity == 'medium':
                        summary['medium'] += 1
                    elif severity == 'low':
                        summary['low'] += 1

                    # Store failed findings
                    summary['findings'].append({
                        'check_id': finding.get('metadata', {}).get('event_code', 'N/A'),
                        'check_title': finding.get('message', 'N/A'),
                        'severity': severity,
                        'status': status_code,
                        'resource': finding.get('resources', [{}])[0].get('uid', 'N/A') if finding.get('resources') else 'N/A',
                        'region': finding.get('cloud', {}).get('region', 'N/A'),
                        'description': finding.get('status_detail', 'N/A'),
                        'remediation': finding.get('remediation', {}).get('desc', 'N/A')
                    })

            return summary

        except Exception as e:
            self.logger.error(f"Error parsing Prowler output: {str(e)}")
            return {
                'error': f"Failed to parse results: {str(e)}",
                'output_dir': str(output_dir)
            }
