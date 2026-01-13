# Cloud Security Scanner - Project Structure

## Overview

This document describes the complete structure of the Cloud Security Scanner implementing Approach 2 (Runtime Scanning).

## Directory Tree

```
cloud_security_scanner/
│
├── scanner.py                      # Main CLI entry point
├── setup.py                        # Package installation script
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview and introduction
├── QUICKSTART.md                   # Quick start guide
├── LICENSE                         # MIT License
├── .gitignore                      # Git ignore rules
│
├── config/                         # Configuration files
│   ├── config.yaml                 # Main configuration
│   └── credentials.yaml.example    # Credential template (DO NOT commit actual credentials!)
│
├── core/                           # Core orchestration logic
│   ├── __init__.py
│   └── orchestrator.py             # Main scanner orchestrator
│
├── scanners/                       # Scanner integrations
│   ├── __init__.py
│   ├── prowler_scanner.py          # Prowler integration (450+ AWS, 200+ Azure, 150+ GCP checks)
│   └── scoutsuite_scanner.py       # ScoutSuite integration
│
├── reports/                        # Report generation
│   ├── __init__.py
│   └── generator.py                # Multi-format report generator (JSON, HTML, TXT)
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── config_loader.py            # Configuration loader
│   ├── credentials.py              # Credential management
│   └── logger.py                   # Logging configuration
│
├── docs/                           # Documentation
│   ├── INSTALLATION.md             # Detailed installation guide
│   ├── USAGE.md                    # Usage guide and examples
│   └── ARCHITECTURE.md             # Architecture and design documentation
│
└── examples/                       # Example scripts
    ├── daily_scan.sh               # Automated daily scan (Linux/Mac)
    ├── daily_scan.bat              # Automated daily scan (Windows)
    ├── scan_aws_only.py            # Programmatic usage example
    └── github_actions_workflow.yml # CI/CD integration example

```

## Runtime Generated Directories

These directories are created when the scanner runs:

```
cloud_security_scanner/
│
├── logs/                           # Scanner logs (auto-created)
│   └── scanner.log
│
├── reports/                        # Scan reports (auto-created)
│   └── scan_YYYYMMDD_HHMMSS/
│       ├── scan_results.json       # Machine-readable results
│       ├── scan_results.html       # Visual web report
│       └── summary.txt             # Quick text summary
│
├── prowler-output/                 # Prowler raw output (auto-created)
│   └── prowler_[provider]_[timestamp]/
│
└── scoutsuite-output/              # ScoutSuite raw output (auto-created)
    └── scoutsuite_[provider]_[timestamp]/
```

## File Descriptions

### Root Level Files

| File | Purpose |
|------|---------|
| `scanner.py` | Main CLI interface - run this to start scans |
| `setup.py` | Python package setup for installation |
| `requirements.txt` | All Python dependencies (Prowler, ScoutSuite, etc.) |
| `README.md` | Project introduction and overview |
| `QUICKSTART.md` | Get started in 5 minutes guide |
| `LICENSE` | MIT License |
| `.gitignore` | Excludes logs, reports, credentials from git |

### Configuration Files (`config/`)

| File | Purpose |
|------|---------|
| `config.yaml` | Main settings: scanners, providers, output formats |
| `credentials.yaml.example` | Template for cloud credentials (copy to credentials.yaml) |

**IMPORTANT**: Never commit `credentials.yaml` to version control!

### Core Modules (`core/`)

| File | Purpose |
|------|---------|
| `orchestrator.py` | Coordinates scanner execution, aggregates results |

### Scanner Modules (`scanners/`)

| File | Purpose |
|------|---------|
| `prowler_scanner.py` | Prowler integration - 450+ AWS, 200+ Azure, 150+ GCP checks |
| `scoutsuite_scanner.py` | ScoutSuite integration - complementary coverage |

### Report Modules (`reports/`)

| File | Purpose |
|------|---------|
| `generator.py` | Generates JSON, HTML, and text reports |

### Utility Modules (`utils/`)

| File | Purpose |
|------|---------|
| `config_loader.py` | Loads and validates YAML configuration |
| `credentials.py` | Manages cloud provider credentials securely |
| `logger.py` | Configures logging to file and console |

### Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `INSTALLATION.md` | Step-by-step installation guide |
| `USAGE.md` | Detailed usage instructions and examples |
| `ARCHITECTURE.md` | System architecture and design |

### Examples (`examples/`)

| File | Purpose |
|------|---------|
| `daily_scan.sh` | Bash script for automated daily scans |
| `daily_scan.bat` | Windows batch script for automated daily scans |
| `scan_aws_only.py` | Python example showing programmatic usage |
| `github_actions_workflow.yml` | CI/CD integration template |

## Key Design Principles

### 1. Modularity
Each scanner (Prowler, ScoutSuite) is isolated in its own module, making it easy to add new scanners or remove existing ones.

### 2. Configuration-Driven
All settings are in YAML files, no hard-coded values. Easy to customize without modifying code.

### 3. Security-First
- Credentials are never logged
- Only read-only access required
- Sensitive files excluded from version control

### 4. Extensibility
- Easy to add new scanners
- Easy to add new cloud providers
- Easy to add new report formats

### 5. User-Friendly
- Clear CLI interface
- Multiple output formats
- Comprehensive documentation
- Ready-to-use examples

## Entry Points

### Command Line
```bash
python scanner.py --provider aws
```

### Programmatic
```python
from core.orchestrator import ScannerOrchestrator
orchestrator = ScannerOrchestrator(config)
results = orchestrator.scan(['aws'])
```

### Scheduled
```bash
# Linux/Mac cron
0 2 * * * /path/to/examples/daily_scan.sh

# Windows Task Scheduler
examples\daily_scan.bat
```

## Output Locations

| Data Type | Location | Format |
|-----------|----------|--------|
| Scan Reports | `reports/scan_*/` | JSON, HTML, TXT |
| Scanner Logs | `logs/scanner.log` | Text |
| Prowler Output | `prowler-output/` | JSON, HTML |
| ScoutSuite Output | `scoutsuite-output/` | JSON, HTML |

## Dependencies

See `requirements.txt` for full list. Key dependencies:

- **prowler** - AWS/Azure/GCP security scanner
- **scoutsuite** - Multi-cloud security auditing
- **click** - CLI framework
- **pyyaml** - Configuration parsing
- **boto3** - AWS SDK
- **azure-identity**, **azure-mgmt-*** - Azure SDKs
- **google-cloud-*** - GCP SDKs

## File Size Estimates

| Component | Typical Size |
|-----------|--------------|
| Source Code | ~50 KB |
| Dependencies | ~500 MB |
| Single Scan Reports | ~10-100 MB |
| Logs | ~1-10 MB/day |

## Version Control

### Included in Git
- All source code (`.py` files)
- Configuration templates (`.example` files)
- Documentation (`.md` files)
- Examples

### Excluded from Git (.gitignore)
- `credentials.yaml` - **CRITICAL: Contains secrets**
- `reports/` - Scan output
- `logs/` - Log files
- `prowler-output/`, `scoutsuite-output/` - Raw scanner output
- `venv/`, `__pycache__/` - Python artifacts

## Deployment Scenarios

### Local Development
```
cloud_security_scanner/
├── venv/                    # Virtual environment
└── [all source files]
```

### Production Server
```
/opt/cloud_security_scanner/
├── [source files]
├── config/credentials.yaml  # Real credentials
└── reports/                 # Persistent storage
```

### CI/CD Pipeline
```
/tmp/scanner/
├── [source files]
└── reports/                 # Uploaded as artifacts
```

## Getting Started

1. **Quick Start**: Read `QUICKSTART.md`
2. **Installation**: See `docs/INSTALLATION.md`
3. **Usage**: See `docs/USAGE.md`
4. **Architecture**: See `docs/ARCHITECTURE.md`

## Support

- Issues: Check `logs/scanner.log`
- Examples: See `examples/` directory
- Questions: Review documentation in `docs/`
