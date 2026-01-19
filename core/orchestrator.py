"""
Scanner Orchestrator - Coordinates multiple scanner tools and aggregates results
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from scanners.prowler_scanner import ProwlerScanner
from scanners.cloudsploit_scanner import CloudSploitScanner
from reports.generator import ReportGenerator


class ScannerOrchestrator:
    """Orchestrates security scans across multiple cloud providers"""

    def __init__(self, config: Dict):
        """
        Initialize the scanner orchestrator

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.results = {}

        # Initialize scanners
        self.prowler = ProwlerScanner(config) if config['scanners']['prowler']['enabled'] else None
        self.cloudsploit = CloudSploitScanner(config) if config['scanners']['cloudsploit']['enabled'] else None

        # Initialize report generator
        self.report_generator = ReportGenerator(config)

        # Create output directories
        self._setup_directories()

    def _setup_directories(self):
        """Create necessary output directories"""
        directories = [
            self.config['output']['reports_dir'],
            'logs'
        ]

        if self.prowler:
            directories.append(self.config['scanners']['prowler']['output_dir'])
        if self.cloudsploit:
            directories.append(self.config['scanners']['cloudsploit']['output_dir'])

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def scan(self, providers: List[str], project_id: Optional[str] = None,
             subscription_id: Optional[str] = None, profile: Optional[str] = None) -> Dict:
        """
        Execute security scans for specified cloud providers

        Args:
            providers: List of cloud providers to scan ('aws', 'azure', 'gcp', or 'all')
            project_id: GCP project ID (optional)
            subscription_id: Azure subscription ID (optional)
            profile: AWS profile name (optional)

        Returns:
            Dictionary containing scan results
        """
        if 'all' in providers:
            providers = ['aws', 'azure', 'gcp']

        self.logger.info(f"Starting security scan for providers: {', '.join(providers)}")
        scan_start = datetime.now()

        for provider in providers:
            if not self.config['providers'][provider]['enabled']:
                self.logger.warning(f"{provider.upper()} is disabled in configuration, skipping")
                continue

            self.logger.info(f"Scanning {provider.upper()}...")
            self.results[provider] = self._scan_provider(provider, project_id, subscription_id, profile)

        scan_duration = (datetime.now() - scan_start).total_seconds()
        self.logger.info(f"Scan completed in {scan_duration:.2f} seconds")

        # Generate consolidated report
        report_path = self.report_generator.generate(self.results)
        self.logger.info(f"Reports generated at: {report_path}")

        return {
            'results': self.results,
            'report_path': report_path,
            'scan_duration': scan_duration,
            'timestamp': scan_start.isoformat()
        }

    def _scan_provider(self, provider: str, project_id: Optional[str] = None,
                      subscription_id: Optional[str] = None, profile: Optional[str] = None) -> Dict:
        """
        Scan a specific cloud provider

        Args:
            provider: Cloud provider name ('aws', 'azure', or 'gcp')
            project_id: GCP project ID (optional)
            subscription_id: Azure subscription ID (optional)
            profile: AWS profile name (optional)

        Returns:
            Dictionary containing scan results for the provider
        """
        provider_results = {
            'provider': provider,
            'prowler': None,
            'cloudsploit': None,
            'summary': {
                'failed': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }

        # Prepare scanner kwargs based on provider
        scan_kwargs = {}
        if provider == 'gcp' and project_id:
            scan_kwargs['project_id'] = project_id
        elif provider == 'azure' and subscription_id:
            scan_kwargs['subscription_id'] = subscription_id
        elif provider == 'aws' and profile:
            scan_kwargs['profile'] = profile

        # Run Prowler scan
        if self.prowler:
            try:
                self.logger.info(f"Running Prowler scan for {provider.upper()}...")
                prowler_results = self.prowler.scan(provider, **scan_kwargs)
                provider_results['prowler'] = prowler_results
                self._update_summary(provider_results['summary'], prowler_results)
            except Exception as e:
                self.logger.error(f"Prowler scan failed for {provider}: {str(e)}")
                provider_results['prowler'] = {'error': str(e)}

        # Run CloudSploit scan
        if self.cloudsploit:
            try:
                self.logger.info(f"Running CloudSploit scan for {provider.upper()}...")
                cloudsploit_results = self.cloudsploit.scan(provider, **scan_kwargs)
                provider_results['cloudsploit'] = cloudsploit_results
                self._update_summary(provider_results['summary'], cloudsploit_results)
            except Exception as e:
                self.logger.error(f"CloudSploit scan failed for {provider}: {str(e)}")
                provider_results['cloudsploit'] = {'error': str(e)}

        return provider_results

    def _update_summary(self, summary: Dict, results: Dict):
        """
        Update summary statistics with scan results

        Args:
            summary: Summary dictionary to update
            results: Scan results to aggregate
        """
        if 'error' in results:
            return

        # Add logic to aggregate results based on scanner output format
        if 'failed' in results:
            summary['failed'] += results.get('failed', 0)
            summary['critical'] += results.get('critical', 0)
            summary['high'] += results.get('high', 0)
            summary['medium'] += results.get('medium', 0)
            summary['low'] += results.get('low', 0)

    def get_summary(self) -> Dict:
        """
        Get overall scan summary

        Returns:
            Dictionary containing summary of all scans
        """
        overall_summary = {
            'failed': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'providers_scanned': []
        }

        for provider, results in self.results.items():
            overall_summary['providers_scanned'].append(provider)
            summary = results.get('summary', {})
            overall_summary['failed'] += summary.get('failed', 0)
            overall_summary['critical'] += summary.get('critical', 0)
            overall_summary['high'] += summary.get('high', 0)
            overall_summary['medium'] += summary.get('medium', 0)
            overall_summary['low'] += summary.get('low', 0)

        return overall_summary
