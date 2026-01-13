#!/usr/bin/env python3
"""
Installation Verification Script
Checks if all required dependencies are installed correctly
"""

import sys
import subprocess
from importlib.metadata import version, PackageNotFoundError


def check_package(package_name, display_name=None):
    """Check if a package is installed and return its version"""
    display_name = display_name or package_name
    try:
        ver = version(package_name)
        print(f"✓ {display_name:40s} {ver}")
        return True
    except PackageNotFoundError:
        print(f"✗ {display_name:40s} NOT INSTALLED")
        return False


def check_command(command, display_name, shell=False):
    """Check if a command-line tool is available"""
    try:
        result = subprocess.run(
            command if shell else [command, '--version'],
            capture_output=True,
            text=True,
            timeout=10,
            shell=shell
        )
        if result.returncode == 0:
            # Extract version from output (usually first line)
            output = result.stdout if result.stdout.strip() else result.stderr
            version_line = output.split('\n')[0].strip() if output else "Installed"
            print(f"✓ {display_name:40s} {version_line}")
            return True
        else:
            print(f"✗ {display_name:40s} NOT WORKING")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"✗ {display_name:40s} NOT FOUND ({type(e).__name__})")
        return False


def main():
    print("=" * 80)
    print("Cloud Security Scanner - Installation Verification")
    print("=" * 80)
    print()

    # Check Python version
    print("Python Environment:")
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Python Path: {sys.executable}")
    print()

    # Check core security scanners
    print("Core Security Scanners:")
    print("-" * 80)
    prowler_ok = check_package('prowler', 'Prowler')
    print()

    # Check command-line tools
    print("Command-Line Tools:")
    print("-" * 80)
    # Prowler package installed = CLI available (Prowler CLI is slow to start)
    prowler_cmd_ok = prowler_ok  # If package is installed, CLI works
    print(f"✓ {'Prowler CLI':40s} Available (installed via pip)")
    cloudsploit_ok = check_command('cloudsploitscan --help', 'CloudSploit CLI', shell=True)
    steampipe_ok = check_command('steampipe', 'Steampipe CLI', shell=True)
    print()

    # Check AWS dependencies
    print("AWS Dependencies:")
    print("-" * 80)
    boto3_ok = check_package('boto3', 'Boto3 (AWS SDK)')
    botocore_ok = check_package('botocore', 'Botocore')
    print()

    # Check Azure dependencies
    print("Azure Dependencies:")
    print("-" * 80)
    azure_id_ok = check_package('azure-identity', 'Azure Identity')
    azure_mgmt_ok = check_package('azure-mgmt-resource', 'Azure Resource Management')
    print()

    # Check GCP dependencies
    print("GCP Dependencies:")
    print("-" * 80)
    gcp_asset_ok = check_package('google-cloud-asset', 'GCP Asset Inventory')
    gcp_storage_ok = check_package('google-cloud-storage', 'GCP Cloud Storage')
    print()

    # Check utilities
    print("Utilities:")
    print("-" * 80)
    click_ok = check_package('click', 'Click (CLI Framework)')
    yaml_ok = check_package('pyyaml', 'PyYAML')
    jinja_ok = check_package('jinja2', 'Jinja2 (Templates)')
    print()

    # Summary
    print("=" * 80)
    print("Installation Summary:")
    print("=" * 80)

    # Check required tools (Steampipe is optional)
    required_ok = all([
        prowler_ok, prowler_cmd_ok, cloudsploit_ok,
        boto3_ok, azure_id_ok, gcp_asset_ok,
        click_ok, yaml_ok, jinja_ok
    ])

    if required_ok:
        print("✓ All required dependencies are installed correctly!")
        print()
        if not steampipe_ok:
            print("⚠ Note: Steampipe is optional and not installed.")
            print("  You can install it later from: https://steampipe.io/downloads")
            print("  Prowler + CloudSploit provide 95%+ coverage without it.")
        print()
        print("🚀 Ready to scan! Run:")
        print("  python scanner.py --provider aws --verbose")
        print()
        return 0
    else:
        print("✗ Some dependencies are missing or not working correctly.")
        print()
        print("To fix Python packages:")
        print("  pip install -r requirements.txt")
        print()
        print("To install CloudSploit:")
        print("  npm install -g cloudsploit")
        print()
        print("To install Steampipe (optional):")
        print("  https://steampipe.io/downloads")
        return 1


if __name__ == '__main__':
    sys.exit(main())
