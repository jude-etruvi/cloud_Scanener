#!/usr/bin/env python3
"""
Example: Scan AWS Only
This script demonstrates how to use the scanner programmatically
"""

import sys
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import ScannerOrchestrator
from utils.logger import setup_logging


def main():
    # Load configuration
    config_file = Path(__file__).parent.parent / 'config' / 'config.yaml'

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Setup logging
    setup_logging(config)

    # Initialize orchestrator
    orchestrator = ScannerOrchestrator(config)

    # Scan AWS only
    print("Starting AWS security scan...")
    results = orchestrator.scan(['aws'])

    # Display summary
    summary = orchestrator.get_summary()

    print("\n" + "=" * 70)
    print("AWS SCAN RESULTS")
    print("=" * 70)
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Failed:       {summary['failed']}")
    print("\nBy Severity:")
    print(f"  Critical:   {summary['critical']}")
    print(f"  High:       {summary['high']}")
    print(f"  Medium:     {summary['medium']}")
    print(f"  Low:        {summary['low']}")
    print(f"\nReports: {results['report_path']}")
    print("=" * 70)

    # Return appropriate exit code
    if summary['critical'] > 0 or summary['high'] > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
