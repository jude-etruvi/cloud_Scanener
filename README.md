# Cloud Security Scanner

Multi-cloud security scanning tool supporting AWS, Azure, and GCP using Prowler and CloudSploit.

## Quick Links

- [Installation Guide](docs/INSTALL_NEW.md)
- [Quick Start](docs/QUICKSTART.md)
- [Usage Guide](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)

## Features

- Multi-cloud support (AWS, Azure, GCP)
- Multiple scanning engines (Prowler, CloudSploit)
- Interactive and CLI modes
- Consolidated reporting
- HTML and JSON output formats

## Quick Install

```bash
# Clone repository
git clone <repository-url>
cd cloud_security_scanner

# Run setup
python setup.py install

# Verify installation
python verify_install.py
```

## Quick Start

```bash
# Interactive mode (recommended for first-time users)
python scanner.py --interactive

# Command-line mode
python scanner.py --provider aws
python scanner.py --provider gcp --project-id my-project
python scanner.py --provider azure --subscription-id 12345
```

## Documentation

Full documentation is available in the [docs](docs/) folder:
- Installation instructions
- Configuration guide
- Usage examples
- Architecture overview

## Output

All scan results are saved to the `reports/` directory with timestamped folders.

## License

See [LICENSE](LICENSE) file for details.
