"""
Steampipe Scanner Integration
SQL-powered cloud infrastructure scanner with compliance frameworks
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SteampipeScanner:
    """Wrapper for Steampipe security scanner"""

    def __init__(self, config: Dict):
        """
        Initialize Steampipe scanner

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(config['scanners']['steampipe']['output_dir'])

    def scan(self, provider: str, **kwargs) -> Dict:
        """
        Execute Steampipe scan for specified cloud provider

        Args:
            provider: Cloud provider ('aws', 'azure', 'gcp')
            **kwargs: Additional provider-specific arguments

        Returns:
            Dictionary containing scan results
        """
        self.logger.info(f"Starting Steampipe scan for {provider.upper()}")

        # Build Steampipe command based on provider
        if provider == 'aws':
            return self._scan_aws(**kwargs)
        elif provider == 'azure':
            return self._scan_azure(**kwargs)
        elif provider == 'gcp':
            return self._scan_gcp(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _scan_aws(self, benchmark: str = 'cis_v200') -> Dict:
        """
        Scan AWS environment using Steampipe benchmarks

        Args:
            benchmark: Benchmark to run (cis_v200, nist_800_53_rev_5, pci_dss_v321, etc.)

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"steampipe_aws_{benchmark}_{timestamp}.json"

        # Build Steampipe command
        cmd = [
            'steampipe',
            'check',
            f'aws_compliance.benchmark.{benchmark}',
            '--output', 'json',
            '--export', str(output_file)
        ]

        # Execute Steampipe
        result = self._execute_steampipe(cmd, output_file, 'aws', benchmark)
        return result

    def _scan_azure(self, benchmark: str = 'cis_v200') -> Dict:
        """
        Scan Azure environment using Steampipe benchmarks

        Args:
            benchmark: Benchmark to run (cis_v200, nist_800_53_rev_5, etc.)

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"steampipe_azure_{benchmark}_{timestamp}.json"

        # Build Steampipe command
        cmd = [
            'steampipe',
            'check',
            f'azure_compliance.benchmark.{benchmark}',
            '--output', 'json',
            '--export', str(output_file)
        ]

        # Execute Steampipe
        result = self._execute_steampipe(cmd, output_file, 'azure', benchmark)
        return result

    def _scan_gcp(self, benchmark: str = 'cis_v200') -> Dict:
        """
        Scan GCP environment using Steampipe benchmarks

        Args:
            benchmark: Benchmark to run (cis_v200, cis_v300, etc.)

        Returns:
            Scan results dictionary
        """
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        output_file = self.output_dir / f"steampipe_gcp_{benchmark}_{timestamp}.json"

        # Build Steampipe command
        cmd = [
            'steampipe',
            'check',
            f'gcp_compliance.benchmark.{benchmark}',
            '--output', 'json',
            '--export', str(output_file)
        ]

        # Execute Steampipe
        result = self._execute_steampipe(cmd, output_file, 'gcp', benchmark)
        return result

    def _execute_steampipe(self, cmd: List[str], output_file: Path, provider: str, benchmark: str) -> Dict:
        """
        Execute Steampipe command and parse results

        Args:
            cmd: Command list to execute
            output_file: File where Steampipe will save output
            provider: Cloud provider name
            benchmark: Benchmark name

        Returns:
            Parsed scan results
        """
        try:
            self.logger.info(f"Executing: {' '.join(cmd)}")

            # Run Steampipe
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if process.returncode != 0:
                self.logger.error(f"Steampipe scan failed: {process.stderr}")
                return {
                    'error': f"Steampipe exited with code {process.returncode}",
                    'stderr': process.stderr,
                    'stdout': process.stdout,
                    'provider': provider,
                    'benchmark': benchmark
                }

            # Parse results
            results = self._parse_steampipe_output(output_file, provider, benchmark)
            return results

        except FileNotFoundError:
            self.logger.error("Steampipe not found. Install from: https://steampipe.io/downloads")
            return {'error': 'Steampipe not installed. Visit: https://steampipe.io/downloads'}
        except subprocess.TimeoutExpired:
            self.logger.error("Steampipe scan timed out")
            return {'error': 'Scan timed out after 1 hour'}
        except Exception as e:
            self.logger.error(f"Error executing Steampipe: {str(e)}")
            return {'error': str(e)}

    def _parse_steampipe_output(self, output_file: Path, provider: str, benchmark: str) -> Dict:
        """
        Parse Steampipe JSON output

        Args:
            output_file: Path to Steampipe output file
            provider: Cloud provider name
            benchmark: Benchmark name

        Returns:
            Parsed results dictionary
        """
        try:
            if not output_file.exists():
                self.logger.warning(f"Steampipe output file not found: {output_file}")
                return {
                    'output_file': str(output_file),
                    'provider': provider,
                    'benchmark': benchmark,
                    'total_checks': 0,
                    'passed': 0,
                    'failed': 0
                }

            self.logger.info(f"Parsing Steampipe results from {output_file}")

            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Aggregate results
            summary = {
                'output_file': str(output_file),
                'provider': provider,
                'benchmark': benchmark,
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'error': 0,
                'alarm': 0,
                'ok': 0,
                'info': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'findings': []
            }

            # Steampipe output structure: groups -> controls -> results
            groups = data.get('groups', [])

            for group in groups:
                controls = group.get('controls', [])
                for control in controls:
                    summary['total_checks'] += 1

                    status = control.get('status', 'error')
                    title = control.get('title', 'N/A')
                    description = control.get('description', '')
                    severity = control.get('severity', 'medium')

                    # Count by status
                    if status == 'ok':
                        summary['passed'] += 1
                        summary['ok'] += 1
                    elif status == 'alarm':
                        summary['failed'] += 1
                        summary['alarm'] += 1

                        # Count by severity
                        if severity.lower() == 'critical':
                            summary['critical'] += 1
                        elif severity.lower() == 'high':
                            summary['high'] += 1
                        elif severity.lower() == 'medium':
                            summary['medium'] += 1
                        elif severity.lower() == 'low':
                            summary['low'] += 1

                        # Store failed finding
                        results = control.get('results', [])
                        for result in results:
                            if result.get('status') == 'alarm':
                                summary['findings'].append({
                                    'control_id': control.get('id', 'N/A'),
                                    'control_title': title,
                                    'severity': severity,
                                    'status': 'fail',
                                    'reason': result.get('reason', 'N/A'),
                                    'resource': result.get('resource', 'N/A'),
                                    'dimensions': result.get('dimensions', {})
                                })
                    elif status == 'skip':
                        summary['skipped'] += 1
                    elif status == 'info':
                        summary['info'] += 1
                    else:
                        summary['error'] += 1

            return summary

        except Exception as e:
            self.logger.error(f"Error parsing Steampipe output: {str(e)}")
            return {
                'error': f"Failed to parse results: {str(e)}",
                'output_file': str(output_file)
            }

    def list_benchmarks(self, provider: str) -> List[str]:
        """
        List available benchmarks for a provider

        Args:
            provider: Cloud provider name

        Returns:
            List of available benchmark names
        """
        # Common benchmarks
        benchmarks = {
            'aws': [
                'cis_v140', 'cis_v150', 'cis_v200',
                'nist_800_53_rev_5', 'nist_csf',
                'pci_dss_v321', 'hipaa_final_omnibus_security_rule_2013',
                'soc_2', 'aws_foundational_security'
            ],
            'azure': [
                'cis_v140', 'cis_v150', 'cis_v200',
                'nist_800_53_rev_5', 'hipaa_hitrust_v92',
                'pci_dss_v321'
            ],
            'gcp': [
                'cis_v100', 'cis_v110', 'cis_v120', 'cis_v200', 'cis_v300',
                'nist_800_53_rev_5'
            ]
        }

        return benchmarks.get(provider, [])
