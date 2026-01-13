#!/usr/bin/env python3
"""
Cloud Security Scanner - Main CLI Interface
Runtime security scanning using Prowler, CloudSploit, and Steampipe
"""

import click
import logging
import sys
import yaml
import os
from pathlib import Path
from datetime import datetime

# Fix Windows Unicode encoding issues
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from core.orchestrator import ScannerOrchestrator
from utils.logger import setup_logging
from utils.config_loader import load_config


def interactive_mode():
    """Interactive mode with step-by-step prompts"""
    click.echo("=" * 70)
    click.echo("Cloud Security Scanner - Interactive Mode")
    click.echo("=" * 70)
    click.echo()

    # Step 1: Select cloud provider
    click.echo("STEP 1: Select Cloud Provider")
    click.echo("-" * 70)
    click.echo("Which cloud provider do you want to scan?")
    click.echo("  1. AWS (Amazon Web Services)")
    click.echo("  2. Azure (Microsoft Azure)")
    click.echo("  3. GCP (Google Cloud Platform)")
    click.echo("  4. All (Scan all providers)")
    click.echo()

    provider_choice = click.prompt("Enter your choice (1-4)", type=int, default=1)
    provider_map = {1: 'aws', 2: 'azure', 3: 'gcp', 4: 'all'}
    provider = provider_map.get(provider_choice, 'aws')

    click.echo(f"\n✓ Selected: {provider.upper()}\n")

    # Step 2: Select scanning tools
    click.echo("STEP 2: Select Scanning Tools")
    click.echo("-" * 70)
    click.echo("Which tools do you want to use?")
    click.echo("  1. Prowler only (Python-based, 800+ checks)")
    click.echo("  2. CloudSploit only (Node.js-based, 700+ checks)")
    click.echo("  3. Prowler + CloudSploit (Recommended - Maximum coverage)")
    click.echo("  4. All tools (Prowler + CloudSploit + Steampipe)")
    click.echo()

    tool_choice = click.prompt("Enter your choice (1-4)", type=int, default=3)

    use_prowler = tool_choice in [1, 3, 4]
    use_cloudsploit = tool_choice in [2, 3, 4]
    use_steampipe = tool_choice == 4

    tools = []
    if use_prowler:
        tools.append("Prowler")
    if use_cloudsploit:
        tools.append("CloudSploit")
    if use_steampipe:
        tools.append("Steampipe")

    click.echo(f"\n✓ Selected tools: {', '.join(tools)}\n")

    # Step 3: Configure credentials
    providers = [provider] if provider != 'all' else ['aws', 'azure', 'gcp']
    credentials_config = {}

    for prov in providers:
        if prov == 'aws':
            credentials_config['aws'] = configure_aws_credentials()
        elif prov == 'azure':
            credentials_config['azure'] = configure_azure_credentials()
        elif prov == 'gcp':
            credentials_config['gcp'] = configure_gcp_credentials()

    # Step 4: Confirm and run
    click.echo("\nSTEP 4: Confirm Configuration")
    click.echo("-" * 70)
    click.echo(f"Cloud Provider(s): {', '.join([p.upper() for p in providers])}")
    click.echo(f"Scanning Tools:    {', '.join(tools)}")
    click.echo("-" * 70)

    if click.confirm("\nProceed with scan?", default=True):
        return provider, use_prowler, use_cloudsploit, use_steampipe, credentials_config, True
    else:
        click.echo("Scan cancelled.")
        sys.exit(0)


def configure_aws_credentials():
    """Configure AWS credentials interactively"""
    click.echo("\nSTEP 3a: Configure AWS Credentials")
    click.echo("-" * 70)
    click.echo("How do you want to provide AWS credentials?")
    click.echo("  1. Use existing AWS profile from ~/.aws/credentials")
    click.echo("  2. Use environment variables (already set)")
    click.echo("  3. Enter credentials manually (will set as environment variables)")
    click.echo("  4. Skip (use default credentials)")
    click.echo()

    cred_choice = click.prompt("Enter your choice (1-4)", type=int, default=1)

    if cred_choice == 1:
        profile = click.prompt("Enter AWS profile name", default="default")
        click.echo(f"✓ Will use AWS profile: {profile}")
        return {'type': 'profile', 'profile': profile}

    elif cred_choice == 2:
        click.echo("✓ Using existing environment variables")
        return {'type': 'env', 'already_set': True}

    elif cred_choice == 3:
        click.echo("\nEnter your AWS credentials:")
        access_key = click.prompt("AWS Access Key ID", hide_input=True)
        secret_key = click.prompt("AWS Secret Access Key", hide_input=True)
        region = click.prompt("AWS Region", default="us-east-1")

        # Set environment variables
        os.environ['AWS_ACCESS_KEY_ID'] = access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        os.environ['AWS_DEFAULT_REGION'] = region

        click.echo("✓ Credentials set as environment variables")
        return {'type': 'manual', 'region': region}

    else:
        click.echo("✓ Using default credentials")
        return {'type': 'default'}


def configure_azure_credentials():
    """Configure Azure credentials interactively"""
    click.echo("\nSTEP 3b: Configure Azure Credentials")
    click.echo("-" * 70)
    click.echo("How do you want to authenticate with Azure?")
    click.echo("  1. Use Azure CLI (az login) - Recommended")
    click.echo("  2. Use environment variables (already set)")
    click.echo("  3. Enter Service Principal credentials manually")
    click.echo("  4. Skip (use default credentials)")
    click.echo()

    cred_choice = click.prompt("Enter your choice (1-4)", type=int, default=1)

    if cred_choice == 1:
        subscription_id = click.prompt("Azure Subscription ID (optional)", default="")
        click.echo("✓ Will use Azure CLI authentication")
        return {'type': 'az_cli', 'subscription_id': subscription_id if subscription_id else None}

    elif cred_choice == 2:
        click.echo("✓ Using existing environment variables")
        return {'type': 'env', 'already_set': True}

    elif cred_choice == 3:
        click.echo("\nEnter your Azure Service Principal credentials:")
        tenant_id = click.prompt("Tenant ID", hide_input=True)
        client_id = click.prompt("Client ID", hide_input=True)
        client_secret = click.prompt("Client Secret", hide_input=True)
        subscription_id = click.prompt("Subscription ID")

        # Set environment variables
        os.environ['AZURE_TENANT_ID'] = tenant_id
        os.environ['AZURE_CLIENT_ID'] = client_id
        os.environ['AZURE_CLIENT_SECRET'] = client_secret
        os.environ['AZURE_SUBSCRIPTION_ID'] = subscription_id

        click.echo("✓ Credentials set as environment variables")
        return {'type': 'manual', 'subscription_id': subscription_id}

    else:
        click.echo("✓ Using default credentials")
        return {'type': 'default'}


def configure_gcp_credentials():
    """Configure GCP credentials interactively"""
    click.echo("\nSTEP 3c: Configure GCP Credentials")
    click.echo("-" * 70)
    click.echo("How do you want to authenticate with GCP?")
    click.echo("  1. Use Application Default Credentials (gcloud auth)")
    click.echo("  2. Use service account key file")
    click.echo("  3. Use environment variables (already set)")
    click.echo("  4. Skip (use default credentials)")
    click.echo()

    cred_choice = click.prompt("Enter your choice (1-4)", type=int, default=1)

    if cred_choice == 1:
        project_id = click.prompt("GCP Project ID")
        click.echo("✓ Will use Application Default Credentials")
        return {'type': 'adc', 'project_id': project_id}

    elif cred_choice == 2:
        key_file = click.prompt("Path to service account key file (JSON)")
        project_id = click.prompt("GCP Project ID")

        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_file

        click.echo("✓ Service account key configured")
        return {'type': 'key_file', 'key_file': key_file, 'project_id': project_id}

    elif cred_choice == 3:
        click.echo("✓ Using existing environment variables")
        return {'type': 'env', 'already_set': True}

    else:
        click.echo("✓ Using default credentials")
        return {'type': 'default'}


@click.command()
@click.option(
    '--interactive',
    '-i',
    is_flag=True,
    help='Run in interactive mode with step-by-step prompts'
)
@click.option(
    '--provider',
    '-p',
    type=click.Choice(['aws', 'azure', 'gcp', 'all'], case_sensitive=False),
    help='Cloud provider to scan'
)
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True),
    default='config/config.yaml',
    help='Path to configuration file'
)
@click.option(
    '--profile',
    help='AWS profile name (for AWS scans)'
)
@click.option(
    '--project-id',
    help='GCP project ID (for GCP scans)'
)
@click.option(
    '--subscription-id',
    help='Azure subscription ID (for Azure scans)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose logging'
)
@click.option(
    '--output-dir',
    '-o',
    type=click.Path(),
    help='Override output directory for reports'
)
def main(interactive, provider, config, profile, project_id, subscription_id, verbose, output_dir):
    """
    Cloud Security Scanner - Runtime scanning for AWS, Azure, and GCP

    Examples:
        scanner.py --interactive           (Interactive mode with step-by-step prompts)
        scanner.py --provider aws          (Command-line mode)
        scanner.py --provider azure --subscription-id 12345
        scanner.py --provider gcp --project-id my-project
        scanner.py --provider all
    """

    # Run interactive mode if requested or if no provider specified
    credentials_config = None
    if interactive or provider is None:
        provider, use_prowler, use_cloudsploit, use_steampipe, credentials_config, verbose_mode = interactive_mode()
        verbose = verbose or verbose_mode

        # Extract project_id, subscription_id, profile from credentials_config
        if credentials_config and 'gcp' in credentials_config:
            project_id = credentials_config['gcp'].get('project_id', project_id)
        if credentials_config and 'azure' in credentials_config:
            subscription_id = credentials_config['azure'].get('subscription_id', subscription_id)
        if credentials_config and 'aws' in credentials_config:
            profile = credentials_config['aws'].get('profile', profile)

    # Load configuration
    try:
        config_data = load_config(config)
    except Exception as e:
        click.echo(f"Error loading configuration: {str(e)}", err=True)
        sys.exit(1)

    # If interactive mode, update config based on user selections
    if interactive or provider is None:
        config_data['scanners']['prowler']['enabled'] = use_prowler
        config_data['scanners']['cloudsploit']['enabled'] = use_cloudsploit
        config_data['scanners']['steampipe']['enabled'] = use_steampipe

    # Override output directory if specified
    if output_dir:
        config_data['output']['reports_dir'] = output_dir

    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(config_data, log_level)
    logger = logging.getLogger(__name__)

    # Display banner
    click.echo()
    click.echo("=" * 70)
    click.echo("Cloud Security Scanner - Runtime Scanning (Approach 2)")
    click.echo("=" * 70)
    click.echo(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Provider(s): {provider.upper()}")
    click.echo("=" * 70)
    click.echo()

    # Determine providers to scan
    providers = [provider.lower()] if provider != 'all' else ['aws', 'azure', 'gcp']

    try:
        # Initialize orchestrator
        orchestrator = ScannerOrchestrator(config_data)

        # Execute scans
        click.echo("Starting security scan...")
        results = orchestrator.scan(providers, project_id=project_id,
                                   subscription_id=subscription_id, profile=profile)

        # Display summary
        click.echo()
        click.echo("=" * 70)
        click.echo("SCAN SUMMARY")
        click.echo("=" * 70)

        summary = orchestrator.get_summary()
        click.echo(f"Providers scanned: {', '.join(summary['providers_scanned'])}")
        click.echo(f"Failed checks:     {summary['failed']}")
        click.echo()
        click.echo("By Severity:")
        click.echo(f"  Critical:        {summary['critical']}")
        click.echo(f"  High:            {summary['high']}")
        click.echo(f"  Medium:          {summary['medium']}")
        click.echo(f"  Low:             {summary['low']}")
        click.echo()
        click.echo(f"Reports saved to:  {results['report_path']}")
        click.echo(f"Scan duration:     {results['scan_duration']:.2f} seconds")
        click.echo("=" * 70)

        # Exit with appropriate code
        if summary['critical'] > 0 or summary['high'] > 0:
            click.echo()
            click.echo("WARNING: Critical or High severity issues found!")
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        click.echo("\nScan interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        logger.exception("Scan failed")
        click.echo(f"\nError: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
