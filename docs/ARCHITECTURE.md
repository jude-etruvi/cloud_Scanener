# Architecture Overview

## System Design

The Cloud Security Scanner implements **Approach 2: Runtime Scanning** from the technical proposal, providing comprehensive security assessment with 90-95% coverage of cloud misconfigurations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                       (scanner.py)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Scanner Orchestrator                        │
│                (core/orchestrator.py)                        │
│  - Coordinates scan execution                                │
│  - Manages scanner instances                                 │
│  - Aggregates results                                        │
└─────┬──────────────────────────────────────────┬────────────┘
      │                                          │
      ▼                                          ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   Prowler Scanner        │    │   ScoutSuite Scanner         │
│ (scanners/prowler_*.py)  │    │ (scanners/scoutsuite_*.py)   │
│                          │    │                              │
│ - AWS: 450+ checks       │    │ - Multi-cloud assessment     │
│ - Azure: 200+ checks     │    │ - Detailed findings          │
│ - GCP: 150+ checks       │    │ - HTML reports               │
└─────────┬────────────────┘    └──────────────┬───────────────┘
          │                                    │
          └────────────┬───────────────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │   Cloud Provider APIs   │
          │  (Read-Only Access)     │
          ├─────────────────────────┤
          │  AWS                    │
          │  Azure                  │
          │  GCP                    │
          └─────────────────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │   Report Generator      │
          │ (reports/generator.py)  │
          │                         │
          │ - JSON reports          │
          │ - HTML reports          │
          │ - Summary reports       │
          └─────────────────────────┘
```

## Component Details

### 1. CLI Interface (`scanner.py`)

**Responsibilities:**
- Parse command-line arguments
- Load configuration
- Initialize logging
- Display user-friendly output

**Key Features:**
- Provider selection (AWS, Azure, GCP, or all)
- Configuration override options
- Verbose logging mode
- Exit codes for CI/CD integration

### 2. Scanner Orchestrator (`core/orchestrator.py`)

**Responsibilities:**
- Initialize scanner instances
- Coordinate scan execution
- Aggregate results from multiple scanners
- Generate consolidated reports

**Workflow:**
1. Load configuration
2. Initialize Prowler and ScoutSuite scanners
3. For each provider:
   - Execute Prowler scan
   - Execute ScoutSuite scan
   - Aggregate results
4. Generate consolidated reports

### 3. Prowler Scanner (`scanners/prowler_scanner.py`)

**Capabilities:**
- Wraps Prowler CLI tool
- Executes provider-specific scans
- Parses JSON output
- Categorizes findings by severity

**Scan Process:**
1. Build Prowler command with appropriate flags
2. Execute scan via subprocess
3. Monitor execution and handle timeouts
4. Parse JSON output
5. Extract and categorize findings

### 4. ScoutSuite Scanner (`scanners/scoutsuite_scanner.py`)

**Capabilities:**
- Wraps ScoutSuite CLI tool
- Provides complementary coverage to Prowler
- Generates detailed HTML reports
- Analyzes security posture

**Scan Process:**
1. Build ScoutSuite command
2. Execute scan via subprocess
3. Parse JavaScript/JSON output
4. Extract findings and statistics

### 5. Report Generator (`reports/generator.py`)

**Output Formats:**
- **JSON**: Machine-readable, complete results
- **HTML**: Visual, interactive web report
- **TXT**: Quick summary for terminal viewing

**Report Contents:**
- Overall summary statistics
- Provider-specific breakdowns
- Findings categorized by severity
- Detailed issue descriptions
- Remediation guidance

### 6. Utility Modules

#### Configuration Loader (`utils/config_loader.py`)
- Loads YAML configuration files
- Validates required settings
- Provides default values

#### Credential Manager (`utils/credentials.py`)
- Manages cloud provider credentials
- Supports multiple authentication methods
- Sets up environment variables

#### Logger (`utils/logger.py`)
- Configures structured logging
- Supports file and console output
- Filters third-party library noise

## Data Flow

```
1. User invokes scanner
   ↓
2. CLI parses arguments and loads config
   ↓
3. Orchestrator initializes scanners
   ↓
4. For each provider:
   a. Prowler scans via cloud APIs
   b. ScoutSuite scans via cloud APIs
   c. Results parsed and aggregated
   ↓
5. Report generator creates outputs
   ↓
6. Reports saved to disk
   ↓
7. Summary displayed to user
```

## Security Design

### Principle of Least Privilege
- Scanner requires only read-only access
- No write permissions needed
- Uses managed IAM policies where possible

### Credential Handling
- Supports multiple authentication methods
- Prefers cloud provider credential chains
- Credentials never logged or included in reports
- Credentials file (.yaml) excluded from version control

### No Data Exfiltration
- All scans run locally or in customer environment
- No data sent to external services
- Reports stored locally

## Scalability Considerations

### Parallel Execution
- Prowler and ScoutSuite can run concurrently
- Multiple providers can be scanned independently
- Future enhancement: Parallel region scanning

### Resource Usage
- Scanner is I/O bound (API calls)
- Memory usage depends on environment size
- Disk usage for temporary scan outputs

### Performance Optimizations
- Configurable scan scope (regions, services)
- Severity threshold filtering
- Incremental scanning (future enhancement)

## Extensibility

### Adding New Scanners
1. Create scanner class in `scanners/`
2. Implement `scan()` method
3. Add to orchestrator initialization
4. Update configuration schema

### Custom Checks
Future enhancement to support custom security policies:
- Define custom check logic
- Integration with scanner frameworks
- Custom severity levels

### Integration Points
- Exit codes for CI/CD pipelines
- JSON output for SIEM integration
- Webhook notifications (future)
- Ticketing system integration (future)

## Coverage Details

### Approach 2 Coverage: 90-95%

**What It Detects:**
- ✓ Missing encryption configurations
- ✓ Public resource exposure
- ✓ Overly permissive IAM policies
- ✓ Missing logging/monitoring
- ✓ Insecure network configurations
- ✓ Certificate expiration
- ✓ Actual network exposure (active testing)
- ✓ Configuration drift
- ✓ Resources created outside IaC
- ✓ Runtime security posture

**Provider-Specific Coverage:**

| Provider | Checks | Quality    | Tools Used           |
|----------|--------|------------|----------------------|
| AWS      | 450+   | Excellent  | Prowler, ScoutSuite  |
| Azure    | 200+   | Good       | Prowler, ScoutSuite  |
| GCP      | 150+   | Basic-Good | Prowler, ScoutSuite  |

## Deployment Models

### Local Execution
- Run from developer workstation
- Good for: Ad-hoc scans, testing

### CI/CD Integration
- Run as part of deployment pipeline
- Good for: Pre-deployment validation

### Scheduled Scans
- Cron job or scheduled task
- Good for: Continuous monitoring, compliance

### Cloud-Native Deployment
- Lambda/Cloud Functions
- Good for: Serverless automation, event-driven
