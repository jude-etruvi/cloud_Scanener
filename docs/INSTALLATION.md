# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Cloud provider CLI tools (optional but recommended):
  - AWS CLI
  - Azure CLI
  - gcloud CLI

## Installation Steps

### 1. Clone or Download the Repository

```bash
cd cloud_security_scanner
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Package

```bash
pip install -e .
```

### 5. Configure Cloud Provider Access

#### AWS Setup

**Option 1: Using AWS CLI (Recommended)**
```bash
aws configure
```

**Option 2: Using IAM Role (for EC2/ECS/Lambda)**
No additional configuration needed if running on AWS infrastructure with proper IAM role attached.

**Option 3: Using credentials file**
Copy `config/credentials.yaml.example` to `config/credentials.yaml` and configure:
```yaml
aws:
  profile: "default"
```

#### Azure Setup

**Option 1: Using Azure CLI (Recommended)**
```bash
az login
```

**Option 2: Using Service Principal**
```bash
az ad sp create-for-rbac --name "SecurityScanner" --role Reader
```

Copy the output to `config/credentials.yaml`:
```yaml
azure:
  tenant_id: "YOUR_TENANT_ID"
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
```

#### GCP Setup

**Option 1: Using Application Default Credentials (Recommended)**
```bash
gcloud auth application-default login
```

**Option 2: Using Service Account**
```bash
gcloud iam service-accounts create security-scanner --display-name "Security Scanner"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:security-scanner@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/viewer"

gcloud iam service-accounts keys create sa-key.json \
    --iam-account=security-scanner@PROJECT_ID.iam.gserviceaccount.com
```

Configure in `config/credentials.yaml`:
```yaml
gcp:
  service_account_key_file: "/path/to/sa-key.json"
```

### 6. Verify Installation

```bash
python scanner.py --help
```

## Required IAM Permissions

### AWS
The scanner requires read-only access. Use the following managed policies:
- `ReadOnlyAccess` (AWS managed policy)
- Or create a custom policy with specific read permissions

### Azure
The scanner requires read-only access:
- `Reader` role at subscription level

### GCP
The scanner requires read-only access:
- `Viewer` role at project level

## Troubleshooting

### Prowler Installation Issues

If Prowler installation fails:
```bash
pip install --upgrade pip
pip install prowler --no-cache-dir
```

### ScoutSuite Installation Issues

If ScoutSuite installation fails:
```bash
pip install scoutsuite --no-cache-dir
```

### Permission Issues

Ensure your credentials have sufficient read permissions for all services you want to scan.

### Network Issues

If running behind a corporate proxy, configure:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## Next Steps

See [USAGE.md](USAGE.md) for detailed usage instructions.
