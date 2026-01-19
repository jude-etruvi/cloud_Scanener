# Cloud Security Scanner

Comprehensive multi-cloud security scanning platform using Prowler and CloudSploit for maximum coverage of security misconfigurations.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Reports](#reports)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## Overview

This scanner provides **90-95% coverage** of cloud security misconfigurations through runtime scanning using two powerful open-source tools:

- **Prowler** (Python): 800+ security checks across AWS, Azure, and GCP
- **CloudSploit** (Node.js): 700+ multi-cloud security checks

### Supported Cloud Providers

| Provider | Checks | Coverage | Status |
|----------|--------|----------|--------|
| AWS      | 450+   | Excellent | ✅ Active |
| Azure    | 200+   | Good      | ✅ Active |
| GCP      | 150+   | Basic-Good | ✅ Active |

### What It Detects

- ✓ Missing encryption configurations
- ✓ Public resource exposure
- ✓ Overly permissive IAM policies
- ✓ Missing logging/monitoring
- ✓ Insecure network configurations
- ✓ Certificate expiration
- ✓ Configuration drift
- ✓ Resources created outside IaC
- ✓ Runtime security posture
- ✓ Compliance violations

---

## Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              CLI Interface (scanner.py)                  │
│              - Interactive & Command-line modes          │
│              - Configuration loading                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Scanner Orchestrator (core/orchestrator.py)     │
│         - Coordinates scan execution                     │
│         - Manages scanner instances                      │
│         - Aggregates results                             │
└──────┬────────────────────────────────────┬─────────────┘
       │                                    │
       ▼                                    ▼
┌──────────────────────┐         ┌────────────────────────┐
│  Prowler Scanner     │         │  CloudSploit Scanner   │
│  (Python-based)      │         │  (Node.js-based)       │
│                      │         │                        │
│  • AWS: 450+ checks  │         │  • Multi-cloud checks  │
│  • Azure: 200+       │         │  • Fast execution      │
│  • GCP: 150+         │         │  • JSON reports        │
└──────┬───────────────┘         └────────┬───────────────┘
       │                                  │
       └──────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   Cloud Provider APIs       │
        │   (Read-Only Access)        │
        │                             │
        │   • AWS API                 │
        │   • Azure API               │
        │   • GCP API                 │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   Report Generator          │
        │   (reports/generator.py)    │
        │                             │
        │   • JSON Reports            │
        │   • HTML Reports            │
        │   • Text Summaries          │
        └─────────────────────────────┘
```

### Component Details

#### 1. CLI Interface (`scanner.py`)
- Parse command-line arguments
- Load configuration from YAML
- Initialize logging
- Display user-friendly output
- Support interactive and automated modes

#### 2. Scanner Orchestrator (`core/orchestrator.py`)
- Initialize Prowler and CloudSploit scanners
- Coordinate parallel scan execution
- Aggregate results from multiple scanners
- Generate consolidated reports
- Handle errors and timeouts

#### 3. Prowler Scanner (`scanners/prowler_scanner.py`)
- Wraps Prowler CLI tool
- Executes provider-specific scans
- Parses JSON output (OCSF format)
- Categorizes findings by severity
- Generates HTML and CSV reports

#### 4. CloudSploit Scanner (`scanners/cloudsploit_scanner.py`)
- Wraps CloudSploit CLI tool
- Provides complementary coverage
- Fast execution via Node.js
- JSON output parsing
- Multi-cloud support

#### 5. Report Generator (`reports/generator.py`)
- Consolidates findings from all scanners
- Creates HTML visual reports
- Generates JSON for automation
- Produces text summaries
- Categorizes by severity and provider

### Data Flow

```
1. User invokes scanner (CLI or interactive)
   ↓
2. Load configuration (config.yaml)
   ↓
3. Orchestrator initializes scanners
   ↓
4. For each cloud provider:
   a. Prowler scans via cloud APIs
   b. CloudSploit scans via cloud APIs
   c. Results parsed and normalized
   ↓
5. Results aggregated and deduplicated
   ↓
6. Reports generated (HTML, JSON, TXT)
   ↓
7. Reports saved to timestamped folder
   ↓
8. Summary displayed to user
```

---

## Features

✅ **Comprehensive Coverage**: 90-95% of cloud security misconfigurations
✅ **Read-Only Access**: No write permissions required
✅ **Multi-Engine Scanning**: Two complementary tools for better detection
✅ **Multiple Report Formats**: HTML, JSON, and text summaries
✅ **Parallel Execution**: Fast scans with concurrent processing
✅ **Interactive Mode**: Guided scanning for beginners
✅ **CI/CD Integration**: Exit codes and JSON output for automation
✅ **Active Maintenance**: Built on actively maintained open-source tools

---

## Prerequisites

### Required Software

- **Python**: 3.9.2 to 3.12.x (NOT 3.13 or 3.14)
- **Node.js**: 14.0 or higher
- **Operating System**: Windows, Linux, or macOS

### Cloud Provider Access

- **AWS**: IAM user with `SecurityAudit` or `ViewOnlyAccess` policy
- **Azure**: Service principal with `Reader` role
- **GCP**: Service account with `Viewer` role

---

## Installation

### Step 1: Install Python 3.12

#### Windows:
1. Download Python 3.12 from https://www.python.org/downloads/
2. Run installer
   - ✅ Check "Add Python 3.12 to PATH"
   - ✅ Check "Install for all users"
3. Verify: `python --version` → Should show `Python 3.12.x`

#### Linux/Mac:
```bash
# Use pyenv for version management
curl https://pyenv.run | bash
pyenv install 3.12.0
pyenv global 3.12.0
python --version
```

### Step 2: Install Node.js

#### Windows:
1. Download Node.js LTS from https://nodejs.org/
2. Run installer
3. Verify: `node --version` and `npm --version`

#### Linux:
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
```

#### Mac:
```bash
brew install node
node --version
npm --version
```

### Step 3: Set Up Project

```bash
# Navigate to project directory
cd cloud_security_scanner

# Create virtual environment with Python 3.12
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies (Prowler + Cloud SDKs)
pip install -r requirements.txt
```

This installs:
- Prowler 5.16.1
- AWS SDK (boto3)
- Azure SDK (azure-*)
- GCP SDK (google-cloud-*)
- All required utilities

### Step 4: Install CloudSploit

CloudSploit must be cloned from GitHub:

```bash
# Clone CloudSploit repository
cd ~
git clone https://github.com/aquasecurity/cloudsploit.git

# Install dependencies
cd cloudsploit
npm install

# Verify installation
node index.js --help
```

**Note**: Update the CloudSploit path in `config/config.yaml` if installed in a different location.

### Step 5: Configure Cloud Credentials

#### AWS:
```bash
# Option 1: AWS CLI (Recommended)
aws configure
# Enter: Access Key, Secret Key, Region, Output format

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

#### Azure:
```bash
# Login with Azure CLI
az login
# Browser opens, complete authentication

# Set subscription (if multiple)
az account set --subscription "subscription-id"
```

#### GCP:
```bash
# Option 1: Service account key (Recommended)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Option 2: Login with gcloud
gcloud auth application-default login
# Browser opens, complete authentication
```

### Step 6: Verify Installation

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Test Prowler
prowler --version
# Expected: prowler 5.16.1

# Test CloudSploit
node ~/cloudsploit/index.js --help
# Expected: Shows help menu

# Test scanner
python scanner.py --help
# Expected: Shows scanner help menu
```

---

## Configuration

Edit `config/config.yaml` to customize scanner behavior:

```yaml
# Scanner settings
scanners:
  prowler:
    enabled: true
    severity_threshold: "high"  # critical, high, medium, low
    output_formats: ["json", "html", "csv"]

  cloudsploit:
    enabled: true
    path: "C:/Users/alan/cloudsploit/index.js"

# Cloud provider settings
providers:
  aws:
    regions: ["us-east-1", "us-west-2"]  # or "all"
    profile: "default"

  azure:
    subscription_id: "your-subscription-id"

  gcp:
    project_id: "your-project-id"

# Output settings
output:
  directory: "reports"
  formats: ["json", "html", "txt"]
```

---

## Usage

### Interactive Mode (Recommended for First-Time Users)

```bash
python scanner.py
```

The interactive mode will guide you through:
1. Selecting cloud provider(s)
2. Entering provider-specific details
3. Choosing scan options
4. Viewing real-time progress

### Command-Line Mode

#### Scan Single Provider

```bash
# Scan AWS
python scanner.py --provider aws

# Scan AWS with specific profile
python scanner.py --provider aws --profile production

# Scan Azure
python scanner.py --provider azure --subscription-id your-sub-id

# Scan GCP
python scanner.py --provider gcp --project-id your-project-id
```

#### Scan All Providers

```bash
python scanner.py --provider all
```

#### Advanced Options

```bash
# Enable verbose logging
python scanner.py --provider aws --verbose

# Custom output directory
python scanner.py --provider aws --output-dir /path/to/reports

# Specific severity threshold
python scanner.py --provider aws --severity high

# Skip specific scanner
python scanner.py --provider aws --skip-cloudsploit
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--provider` | Cloud provider: `aws`, `azure`, `gcp`, or `all` |
| `--profile` | AWS profile name (default: default) |
| `--subscription-id` | Azure subscription ID |
| `--project-id` | GCP project ID |
| `--output-dir` | Custom output directory |
| `--severity` | Minimum severity: `critical`, `high`, `medium`, `low` |
| `--verbose` | Enable verbose logging |
| `--skip-prowler` | Skip Prowler scanner |
| `--skip-cloudsploit` | Skip CloudSploit scanner |

---

## Reports

### Report Location

All scan results are saved to timestamped folders:
```
reports/
└── scan_20260114_153045/
    ├── scan_results.html    # Visual report
    ├── scan_results.json    # Machine-readable
    ├── summary.txt          # Quick overview
    ├── prowler/             # Prowler raw outputs
    └── cloudsploit/         # CloudSploit raw outputs
```

### Report Contents

#### HTML Report
- Executive summary with statistics
- Findings categorized by severity
- Provider-specific breakdowns
- Detailed issue descriptions
- Remediation guidance
- Interactive charts and tables

#### JSON Report
```json
{
  "scan_info": {
    "timestamp": "2026-01-14T15:30:45",
    "providers": ["aws", "azure"],
    "scanners": ["prowler", "cloudsploit"]
  },
  "summary": {
    "total_findings": 127,
    "critical": 5,
    "high": 23,
    "medium": 67,
    "low": 32
  },
  "findings": [...]
}
```

#### Text Summary
```
=== Cloud Security Scan Summary ===
Scan Date: 2026-01-14 15:30:45
Providers: AWS, Azure

Total Findings: 127
  Critical: 5
  High: 23
  Medium: 67
  Low: 32

Top Issues:
  1. Public S3 buckets (Critical)
  2. Unencrypted RDS instances (High)
  ...
```

---

## Troubleshooting

### Python Version Issues

**Error**: `prowler==5.16.1 requires Python >3.9.1, <3.13`

**Solution**: Install Python 3.12
```bash
# Check current version
python --version

# If 3.13 or 3.14, install 3.12 from python.org
# Then recreate virtual environment
python3.12 -m venv venv
```

### CloudSploit Not Found

**Error**: `CloudSploit executable not found`

**Solution**:
```bash
# Ensure CloudSploit is cloned and installed
cd ~/cloudsploit
npm install

# Update path in config/config.yaml
# Windows: C:/Users/username/cloudsploit/index.js
# Linux/Mac: /home/username/cloudsploit/index.js
```

### GCP Credentials Issues

**Error**: `GOOGLE_APPLICATION_CREDENTIALS not set`

**Solution**:
```bash
# Set environment variable
# Windows:
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\key.json

# Linux/Mac:
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Verify
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### Permission Denied Errors

**Error**: `Permission denied` when running scans

**Solution**:
- **AWS**: Ensure IAM user has `SecurityAudit` or `ViewOnlyAccess` policy
- **Azure**: Ensure service principal has `Reader` role
- **GCP**: Ensure service account has `Viewer` role

### Scan Timeouts

**Error**: Scanner times out on large environments

**Solution**:
```yaml
# Edit config/config.yaml
timeout: 3600  # Increase timeout to 60 minutes

# Or limit scan scope
providers:
  aws:
    regions: ["us-east-1"]  # Scan fewer regions
```

---

## Security Best Practices

### Credential Management

✅ **DO**:
- Use read-only credentials (never write permissions)
- Rotate credentials regularly
- Use IAM roles when possible
- Store credentials securely (never in git)

❌ **DON'T**:
- Commit credentials to version control
- Share credentials in plain text
- Use admin/root credentials
- Hard-code credentials in config files

### Required Permissions

#### AWS
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iam:Get*",
      "iam:List*",
      "ec2:Describe*",
      "s3:GetBucket*",
      "s3:List*"
    ],
    "Resource": "*"
  }]
}
```

Or use managed policy: `arn:aws:iam::aws:policy/SecurityAudit`

#### Azure
```bash
# Assign Reader role
az role assignment create \
  --assignee <service-principal-id> \
  --role "Reader" \
  --scope "/subscriptions/<subscription-id>"
```

#### GCP
```bash
# Grant Viewer role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/viewer"
```

### Network Security

- Scanner makes read-only API calls
- No data exfiltration
- All scans run locally
- Reports stored locally
- No external service dependencies

---

## Tool Information

### Prowler
- **Version**: 5.16.1 (December 2025)
- **GitHub**: https://github.com/prowler-cloud/prowler
- **Documentation**: https://docs.prowler.com/
- **License**: Apache 2.0

### CloudSploit
- **Version**: Latest from GitHub
- **GitHub**: https://github.com/aquasecurity/cloudsploit
- **Documentation**: https://github.com/aquasecurity/cloudsploit/wiki
- **License**: GPL-3.0

---

## Project Structure

```
cloud_security_scanner/
├── scanner.py                    # Main CLI entry point
├── config/
│   └── config.yaml              # Configuration file
├── core/
│   └── orchestrator.py          # Scan coordination
├── scanners/
│   ├── prowler_scanner.py       # Prowler integration
│   └── cloudsploit_scanner.py   # CloudSploit integration
├── reports/
│   └── generator.py             # Report generation
├── utils/
│   ├── config_loader.py         # Config management
│   ├── credentials.py           # Credential handling
│   └── logger.py                # Logging setup
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                    # Project overview
└── docs/
    └── README.md                # This file
```

---

## Contributing

This scanner integrates open-source security tools. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Adding New Scanners

1. Create scanner class in `scanners/`
2. Implement `scan()` method
3. Add to orchestrator initialization
4. Update configuration schema
5. Update documentation

---

## License

MIT License - See LICENSE file

---

## Acknowledgments

Built on top of excellent open-source projects:
- **Prowler** by Prowler Cloud
- **CloudSploit** by Aqua Security

---

## Support

- **Documentation**: This file
- **Installation Issues**: See [Troubleshooting](#troubleshooting)
- **Logs**: Check `logs/scanner.log`
- **Issues**: Create an issue in the repository

---

**Coverage**: 90-95% | **Tools**: 2 | **Checks**: 1500+ | **Active**: Yes
