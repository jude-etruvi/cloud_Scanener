# HTML Report Maker

This module generates professional HTML reports from cloud security scan JSON results.

## Features

- Clean, responsive HTML design
- Executive summary with risk level assessment
- Severity breakdown (Critical, High, Medium, Low)
- Provider-specific details
- Scanner-specific results (Prowler and CloudSploit)
- Top findings display with color-coded severity badges
- Mobile-friendly responsive design

## Usage

### As a Module

```python
from html_report_maker.report_generator import HTMLReportGenerator

generator = HTMLReportGenerator()
output_file = generator.generate_report('path/to/scan_results.json')
print(f"Report generated: {output_file}")
```

### Command Line

```bash
# Generate HTML report from JSON file
python html_report_maker/report_generator.py path/to/scan_results.json

# Specify custom output file
python html_report_maker/report_generator.py path/to/scan_results.json -o custom_report.html
```

## Input Format

The module expects a JSON file with the following structure:

```json
{
  "timestamp": "2024-01-14T10:00:00",
  "scan_duration": 120.5,
  "results": {
    "gcp": {
      "summary": {
        "failed": 10,
        "critical": 2,
        "high": 3,
        "medium": 3,
        "low": 2
      },
      "prowler": {
        "findings": [...]
      },
      "cloudsploit": {
        "findings": [...]
      }
    }
  }
}
```

## Output

The module generates a standalone HTML file with:
- Embedded CSS (no external dependencies)
- Interactive JavaScript features
- Professional color scheme
- Print-friendly layout

## Customization

You can customize the report by modifying:
- `_get_css()`: Change colors, fonts, layout
- `_generate_*()` methods: Modify section content
- `_calculate_risk_level()`: Adjust risk assessment logic
