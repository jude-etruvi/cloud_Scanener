# Installation Guide - Prowler + CloudSploit + Steampipe

Complete setup instructions for the Cloud Security Scanner with the modern stack.

## System Requirements

- **Python**: 3.9.2 to 3.12.x (NOT 3.13 or 3.14)
- **Node.js**: 14.0 or higher (for CloudSploit)
- **PostgreSQL**: 12+ (for Steampipe)
- **Operating System**: Windows, Linux, or macOS

## Step 1: Install Python 3.12

### Windows:
1. Download Python 3.12 from https://www.python.org/downloads/
2. Run installer
   - ✅ Check "Add Python 3.12 to PATH"
   - ✅ Check "Install for all users"
3. Verify: `python --version` → Should show `Python 3.12.x`

### Linux/Mac:
```bash
# Use pyenv for version management
curl https://pyenv.run | bash
pyenv install 3.12.0
pyenv global 3.12.0
python --version
```

## Step 2: Install Node.js

### Windows:
1. Download Node.js LTS from https://nodejs.org/
2. Run installer
3. Verify: `node --version` and `npm --version`

### Linux:
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
```

### Mac:
```bash
brew install node
node --version
npm --version
```

## Step 3: Install Steampipe

### Windows:
```powershell
# Using Chocolatey
choco install steampipe

# Or download installer from https://steampipe.io/downloads
```

### Linux:
```bash
# Download and install
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"

# Verify
steampipe --version
```

### Mac:
```bash
brew install turbot/tap/steampipe
steampipe --version
```

## Step 4: Set Up Project

```bash
# Navigate to project
cd c:\Users\alan\Desktop\cloud_security_scanner

# Create virtual environment with Python 3.12
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies (Prowler + SDKs)
pip install -r requirements.txt
```

This installs:
- Prowler 5.16.1
- AWS SDK (boto3)
- Azure SDK (azure-*)
- GCP SDK (google-cloud-*)
- All utilities

## Step 5: Install CloudSploit

```bash
# Install globally via npm
npm install -g cloudsploit

# Verify installation
cloudsploit --version
```

## Step 6: Install Steampipe Plugins

```bash
# Install cloud provider plugins
steampipe plugin install aws
steampipe plugin install azure
steampipe plugin install gcp

# Install compliance plugins
steampipe plugin install aws_compliance
steampipe plugin install azure_compliance
steampipe plugin install gcp_compliance

# Verify plugins
steampipe plugin list
```

## Step 7: Configure Cloud Credentials

### AWS:
```bash
# Option 1: AWS CLI
aws configure
# Enter: Access Key, Secret Key, Region, Output format

# Option 2: Environment variables
set AWS_ACCESS_KEY_ID=your_key
set AWS_SECRET_ACCESS_KEY=your_secret
set AWS_DEFAULT_REGION=us-east-1
```

### Azure:
```bash
# Login with Azure CLI
az login
# Browser opens, complete authentication
```

### GCP:
```bash
# Login with gcloud
gcloud auth application-default login
# Browser opens, complete authentication

# Or set service account key
set GOOGLE_APPLICATION_CREDENTIALS=path\to\key.json
```

## Step 8: Verify Installation

```bash
# Activate venv if not already
venv\Scripts\activate

# Run verification script
python verify_install.py
```

Expected output:
```
✓ Prowler                                5.16.1
✓ Prowler CLI                            prowler 5.16.1
✓ CloudSploit CLI                        cloudsploit 2.x.x
✓ Steampipe CLI                          steampipe 0.x.x
✓ Boto3 (AWS SDK)                        1.35.76
✓ Azure Identity                         1.19.0
✓ GCP Asset                              3.26.3
✓ All core dependencies are installed correctly!
```

## Step 9: Run Your First Scan

```bash
# Scan AWS only
python scanner.py --provider aws --verbose

# Scan all providers
python scanner.py --provider all --verbose
```

## Troubleshooting

### Python Version Issues

**Error**: `prowler==5.16.1` requires Python >3.9.1, <3.13

**Solution**: Install Python 3.12
```bash
# Check current version
python --version

# If 3.14 or 3.13, install 3.12
# Download from python.org and reinstall
```

### CloudSploit Not Found

**Error**: `cloudsploit: command not found`

**Solution**:
```bash
# Install globally
npm install -g cloudsploit

# If permission error (Linux/Mac):
sudo npm install -g cloudsploit

# Verify
cloudsploit --version
```

### Steampipe Not Found

**Error**: `steampipe: command not found`

**Solution**:
```bash
# Windows (run as Administrator):
choco install steampipe

# Linux:
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"

# Mac:
brew install turbot/tap/steampipe

# Verify
steampipe --version
```

### Steampipe Connection Issues

**Error**: `connection "aws" not found`

**Solution**:
```bash
# Configure Steampipe connections
steampipe service start

# Edit connection config
# Windows: %USERPROFILE%\.steampipe\config\aws.spc
# Linux/Mac: ~/.steampipe/config/aws.spc

# Add AWS connection
connection "aws" {
  plugin = "aws"
  regions = ["*"]
}
```

### Permission Denied Errors

**Windows**: Run terminal as Administrator

**Linux/Mac**:
```bash
sudo chmod +x /path/to/file
# Or use sudo for installation commands
```

## Post-Installation

### Update scanners regularly:
```bash
# Update Prowler
pip install --upgrade prowler

# Update CloudSploit
npm update -g cloudsploit

# Update Steampipe
steampipe plugin update --all
```

### Configure scanner options:
Edit `config/config.yaml` to:
- Enable/disable specific scanners
- Change severity thresholds
- Specify regions/subscriptions/projects
- Set output formats

## Tool Versions

As of 2026-01-09:
- **Prowler**: 5.16.1 (Dec 23, 2025)
- **CloudSploit**: Latest from npm
- **Steampipe**: Latest from brew/apt

## Architecture

```
Python (Prowler) + Node.js (CloudSploit) + PostgreSQL (Steampipe)
                            ↓
              Scanner Orchestrator (Python)
                            ↓
          Reports (JSON, HTML, TXT)
```

## Next Steps

1. Review configuration: `config/config.yaml`
2. Run first scan: `python scanner.py --provider aws`
3. View reports: `reports/scan_*/scan_results.html`
4. Read full documentation: `docs/USAGE.md`

## Getting Help

- Prowler docs: https://docs.prowler.com/
- CloudSploit docs: https://github.com/aquasecurity/cloudsploit
- Steampipe docs: https://steampipe.io/docs

## Security Note

All scanners only require **READ-ONLY** access:
- AWS: `ReadOnlyAccess` or `SecurityAudit` policy
- Azure: `Reader` role
- GCP: `Viewer` role

Never provide write permissions!
