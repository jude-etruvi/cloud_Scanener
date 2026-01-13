# Usage Guide

## Basic Usage

### Scan All Providers

```bash
python scanner.py --provider all
```

### Scan Specific Provider

```bash
# AWS only
python scanner.py --provider aws

# Azure only
python scanner.py --provider azure

# GCP only
python scanner.py --provider gcp
```

## Advanced Usage

### AWS Specific Options

```bash
# Use specific AWS profile
python scanner.py --provider aws --profile production

# Scan specific regions (modify config.yaml)
# Set providers.aws.regions to ["us-east-1", "us-west-2"]
```

### Azure Specific Options

```bash
# Scan specific subscription
python scanner.py --provider azure --subscription-id YOUR_SUBSCRIPTION_ID
```

### GCP Specific Options

```bash
# Scan specific project
python scanner.py --provider gcp --project-id YOUR_PROJECT_ID
```

### Output Options

```bash
# Custom output directory
python scanner.py --provider all --output-dir /path/to/reports

# Verbose logging
python scanner.py --provider all --verbose
```

### Configuration File

```bash
# Use custom configuration file
python scanner.py --provider all --config /path/to/config.yaml
```

## Understanding the Output

### Console Output

The scanner displays:
- Real-time progress of the scan
- Summary of findings by severity
- Total checks passed/failed
- Location of detailed reports

Example output:
```
======================================================================
Cloud Security Scanner - Runtime Scanning (Approach 2)
======================================================================
Timestamp: 2024-01-15 10:30:00
Provider(s): ALL
======================================================================

Starting security scan...
INFO: Starting Prowler scan for AWS...
INFO: Starting ScoutSuite scan for AWS...

======================================================================
SCAN SUMMARY
======================================================================
Providers scanned: aws, azure, gcp
Total checks:      800
Passed:            720
Failed:            80

By Severity:
  Critical:        5
  High:            15
  Medium:          35
  Low:             25

Reports saved to:  reports/scan_20240115_103000
Scan duration:     245.32 seconds
======================================================================
```

### Report Files

The scanner generates three types of reports in the output directory:

1. **JSON Report** (`scan_results.json`)
   - Complete machine-readable results
   - Includes all findings with full details
   - Suitable for integration with other tools

2. **HTML Report** (`scan_results.html`)
   - Visual, interactive report
   - Open in web browser
   - Organized by provider and severity
   - Includes charts and summaries

3. **Summary Report** (`summary.txt`)
   - Quick text overview
   - Easy to read in terminal
   - High-level statistics

## Configuration

### Main Configuration (`config/config.yaml`)

```yaml
output:
  reports_dir: "reports"
  format: ["json", "html"]

scanners:
  prowler:
    enabled: true
    severity_threshold: "medium"  # low, medium, high, critical

  scoutsuite:
    enabled: true

providers:
  aws:
    enabled: true
    regions: "all"  # or ["us-east-1", "us-west-2"]
    services: "all"  # or ["s3", "ec2", "iam"]

  azure:
    enabled: true

  gcp:
    enabled: true

logging:
  level: "INFO"
  file: "logs/scanner.log"
  console: true
```

### Credentials Configuration (`config/credentials.yaml`)

See [INSTALLATION.md](INSTALLATION.md) for credential setup.

## Common Workflows

### Daily Security Scan

```bash
#!/bin/bash
# daily-scan.sh

# Run scan
python scanner.py --provider all --output-dir reports/daily/$(date +%Y%m%d)

# Check exit code
if [ $? -eq 0 ]; then
    echo "Scan completed successfully - no critical/high issues"
else
    echo "Scan found critical/high issues - review reports"
    # Send alert, email, etc.
fi
```

### Scan Before Deployment

```bash
# Pre-deployment security check
python scanner.py --provider aws --profile production --verbose
```

### Compliance Audit

```bash
# Generate compliance report
python scanner.py --provider all --output-dir compliance/audit-$(date +%Y%m%d)
```

## Filtering Results

### By Severity

Modify `config.yaml` to set severity threshold:
```yaml
scanners:
  prowler:
    severity_threshold: "high"  # Only show high and critical
```

### By Service

Scan only specific services:
```yaml
providers:
  aws:
    services: ["s3", "ec2", "rds", "iam"]
```

### By Region

Scan only specific regions:
```yaml
providers:
  aws:
    regions: ["us-east-1", "eu-west-1"]
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run security scan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          python scanner.py --provider aws

      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: security-reports
          path: reports/
```

## Troubleshooting

### Scan Takes Too Long

- Reduce scope by scanning specific regions or services
- Run scans in parallel for different providers
- Disable one of the scanners (Prowler or ScoutSuite)

### Authentication Errors

- Verify credentials are correctly configured
- Check IAM permissions
- Ensure cloud provider CLI tools are working (`aws sts get-caller-identity`, `az account show`, `gcloud auth list`)

### Missing Checks

- Ensure both Prowler and ScoutSuite are enabled
- Check that the severity threshold isn't too high
- Verify the provider configuration includes all desired services

## Best Practices

1. **Regular Scans**: Run daily or weekly scans
2. **Version Control**: Track changes in security posture over time
3. **Alert on Critical**: Set up notifications for critical findings
4. **Review Reports**: Don't just scan - actually review and remediate
5. **Least Privilege**: Use read-only credentials
6. **Secure Storage**: Keep credentials and reports secure
7. **Update Regularly**: Keep Prowler and ScoutSuite updated for latest checks
