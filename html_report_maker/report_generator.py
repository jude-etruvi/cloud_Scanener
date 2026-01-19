"""
HTML Report Generator
Creates professional HTML security reports from JSON scan results
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class HTMLReportGenerator:
    """Generates HTML reports from security scan results"""

    def __init__(self):
        """Initialize the HTML report generator"""
        self.logger = logging.getLogger(__name__)

    def generate_report(self, json_file: str, output_file: Optional[str] = None) -> str:
        """
        Generate HTML report from JSON scan results

        Args:
            json_file: Path to input JSON file
            output_file: Path to output HTML file (optional)

        Returns:
            Path to generated HTML report
        """
        self.logger.info(f"Generating HTML report from {json_file}")

        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Determine output file path
        if not output_file:
            json_path = Path(json_file)
            output_file = str(json_path.parent / f"{json_path.stem}.html")

        # Generate HTML content
        html_content = self._generate_html(data)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"HTML report generated: {output_file}")
        return output_file

    def _generate_html(self, data: Dict) -> str:
        """
        Generate HTML content from scan data

        Args:
            data: Scan results dictionary

        Returns:
            HTML content as string
        """
        # Extract summary data
        summary = self._extract_summary(data)
        providers = self._extract_providers(data)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Security Scan Report</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header(summary)}
        {self._generate_summary_section(summary)}
        {self._generate_providers_section(providers)}
        {self._generate_footer()}
    </div>
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        return html

    def _extract_summary(self, data: Dict) -> Dict:
        """Extract summary information from scan data"""
        summary = {
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'scan_duration': data.get('scan_duration', 0),
            'total_checks': 0,
            'passed': 0,
            'failed': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'providers_scanned': []
        }

        # Handle both old format (with 'results' key) and new format (providers as top-level keys)
        results = data.get('results', data)

        for provider, provider_data in results.items():
            # Skip non-provider keys
            if provider in ['timestamp', 'scan_duration', 'report_path']:
                continue

            summary['providers_scanned'].append(provider.upper())
            provider_summary = provider_data.get('summary', {})
            summary['failed'] += provider_summary.get('failed', 0)
            summary['critical'] += provider_summary.get('critical', 0)
            summary['high'] += provider_summary.get('high', 0)
            summary['medium'] += provider_summary.get('medium', 0)
            summary['low'] += provider_summary.get('low', 0)

        return summary

    def _extract_providers(self, data: Dict) -> List[Dict]:
        """Extract provider-specific results"""
        providers = []

        # Handle both old format (with 'results' key) and new format (providers as top-level keys)
        results = data.get('results', data)

        for provider, provider_data in results.items():
            # Skip non-provider keys
            if provider in ['timestamp', 'scan_duration', 'report_path']:
                continue

            provider_info = {
                'name': provider.upper(),
                'summary': provider_data.get('summary', {}),
                'prowler': provider_data.get('prowler', {}),
                'cloudsploit': provider_data.get('cloudsploit', {})
            }
            providers.append(provider_info)

        return providers

    def _generate_header(self, summary: Dict) -> str:
        """Generate HTML header section"""
        timestamp = datetime.fromisoformat(summary['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        return f"""
        <header>
            <h1>Cloud Security Scan Report</h1>
            <p class="subtitle">Generated on {timestamp}</p>
        </header>"""

    def _generate_summary_section(self, summary: Dict) -> str:
        """Generate summary section HTML"""
        providers_list = ', '.join(summary['providers_scanned'])
        duration = f"{summary['scan_duration']:.2f}"

        # Calculate risk level
        risk_level = self._calculate_risk_level(summary)
        risk_class = risk_level.lower().replace(' ', '-')

        return f"""
        <section class="summary">
            <h2>Executive Summary</h2>
            <div class="summary-cards">
                <div class="card risk-card {risk_class}">
                    <h3>Overall Risk</h3>
                    <div class="risk-level">{risk_level}</div>
                </div>
                <div class="card">
                    <h3>Providers Scanned</h3>
                    <div class="stat-value">{providers_list}</div>
                </div>
                <div class="card">
                    <h3>Scan Duration</h3>
                    <div class="stat-value">{duration}s</div>
                </div>
            </div>

            <div class="severity-breakdown">
                <h3>Findings by Severity</h3>
                <div class="severity-grid">
                    <div class="severity-card critical">
                        <div class="severity-label">Critical</div>
                        <div class="severity-count">{summary['critical']}</div>
                    </div>
                    <div class="severity-card high">
                        <div class="severity-label">High</div>
                        <div class="severity-count">{summary['high']}</div>
                    </div>
                    <div class="severity-card medium">
                        <div class="severity-label">Medium</div>
                        <div class="severity-count">{summary['medium']}</div>
                    </div>
                    <div class="severity-card low">
                        <div class="severity-label">Low</div>
                        <div class="severity-count">{summary['low']}</div>
                    </div>
                </div>
            </div>
        </section>"""

    def _generate_providers_section(self, providers: List[Dict]) -> str:
        """Generate providers section HTML"""
        html = '<section class="providers"><h2>Provider Details</h2>'

        for provider in providers:
            html += self._generate_provider_card(provider)

        html += '</section>'
        return html

    def _generate_provider_card(self, provider: Dict) -> str:
        """Generate HTML for a single provider"""
        name = provider['name']
        summary = provider['summary']

        # Generate scanner results
        prowler_html = self._generate_scanner_results('Prowler', provider['prowler'])
        cloudsploit_html = self._generate_scanner_results('CloudSploit', provider['cloudsploit'])

        return f"""
        <div class="provider-card">
            <h3>{name}</h3>
            <div class="provider-summary">
                <div class="stat">
                    <span class="stat-label">Failed Checks:</span>
                    <span class="stat-value">{summary.get('failed', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Critical:</span>
                    <span class="stat-value critical-text">{summary.get('critical', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">High:</span>
                    <span class="stat-value high-text">{summary.get('high', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Medium:</span>
                    <span class="stat-value medium-text">{summary.get('medium', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Low:</span>
                    <span class="stat-value low-text">{summary.get('low', 0)}</span>
                </div>
            </div>

            <div class="scanner-results">
                {prowler_html}
                {cloudsploit_html}
            </div>
        </div>"""

    def _generate_scanner_results(self, scanner_name: str, scanner_data: Dict) -> str:
        """Generate HTML for scanner results"""
        if not scanner_data or 'error' in scanner_data:
            error_msg = scanner_data.get('error', 'No data available') if scanner_data else 'Not executed'
            return f"""
            <div class="scanner-section">
                <h4>{scanner_name}</h4>
                <div class="error-message">{error_msg}</div>
            </div>"""

        findings = scanner_data.get('findings', [])
        findings_count = len(findings)

        # Show all findings
        findings_html = ''
        for finding in findings:
            findings_html += self._generate_finding_row(finding, scanner_name)

        return f"""
        <div class="scanner-section">
            <h4>{scanner_name}</h4>
            <div class="findings-summary">
                <span>Total Findings: {findings_count}</span>
            </div>
            {f'<div class="findings-table">{findings_html}</div>' if findings_html else '<p>No failed checks found</p>'}
        </div>"""

    def _generate_finding_row(self, finding: Dict, scanner: str) -> str:
        """Generate HTML for a single finding"""
        severity = finding.get('severity', 'unknown').lower()

        # Handle different scanner formats
        if scanner == 'Prowler':
            title = finding.get('check_title', 'N/A')
            resource = finding.get('resource', 'N/A')
            region = finding.get('region', 'N/A')
            description = finding.get('description', '')
            remediation = finding.get('remediation', '')
        else:  # CloudSploit
            title = finding.get('title', 'N/A')
            resource = finding.get('resource', 'N/A')
            region = finding.get('region', 'N/A')
            description = finding.get('message', '')
            remediation = finding.get('remediation', '')

        # Build remediation section if available
        remediation_html = ''
        if remediation and remediation != 'N/A':
            remediation_html = f'''
                <div class="finding-remediation">
                    <strong>Remediation:</strong> {remediation}
                </div>'''

        # Build description section if available
        description_html = ''
        if description and description != 'N/A' and description != title:
            description_html = f'''
                <div class="finding-description">
                    {description}
                </div>'''

        return f"""
        <div class="finding-row">
            <span class="severity-badge {severity}">{severity.upper()}</span>
            <div class="finding-details">
                <div class="finding-title">{title}</div>
                <div class="finding-meta">
                    <span>Resource: {resource}</span>
                    <span>Region: {region}</span>
                </div>
                {description_html}
                {remediation_html}
            </div>
        </div>"""

    def _generate_footer(self) -> str:
        """Generate HTML footer"""
        return """
        <footer>
            <p>Generated by Cloud Security Scanner</p>
        </footer>"""

    def _calculate_risk_level(self, summary: Dict) -> str:
        """Calculate overall risk level based on findings"""
        if summary['critical'] > 0:
            return 'Critical Risk'
        elif summary['high'] >= 5:
            return 'High Risk'
        elif summary['high'] > 0 or summary['medium'] >= 10:
            return 'Medium Risk'
        elif summary['medium'] > 0 or summary['low'] > 0:
            return 'Low Risk'
        else:
            return 'No Issues'

    def _get_css(self) -> str:
        """Return CSS styles for the HTML report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .summary {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .summary h2 {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
        }

        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .card h3 {
            font-size: 0.9em;
            text-transform: uppercase;
            color: #7f8c8d;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }

        .risk-card {
            border-left-width: 6px;
        }

        .risk-card.critical-risk {
            border-left-color: #e74c3c;
            background: #ffebee;
        }

        .risk-card.high-risk {
            border-left-color: #e67e22;
            background: #fff3e0;
        }

        .risk-card.medium-risk {
            border-left-color: #f39c12;
            background: #fff9e6;
        }

        .risk-card.low-risk {
            border-left-color: #3498db;
            background: #e3f2fd;
        }

        .risk-card.no-issues {
            border-left-color: #27ae60;
            background: #e8f5e9;
        }

        .risk-level {
            font-size: 1.8em;
            font-weight: bold;
        }

        .critical-risk .risk-level { color: #e74c3c; }
        .high-risk .risk-level { color: #e67e22; }
        .medium-risk .risk-level { color: #f39c12; }
        .low-risk .risk-level { color: #3498db; }
        .no-issues .risk-level { color: #27ae60; }

        .severity-breakdown h3 {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #2c3e50;
        }

        .severity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .severity-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
        }

        .severity-card.critical { background: linear-gradient(135deg, #e74c3c, #c0392b); }
        .severity-card.high { background: linear-gradient(135deg, #e67e22, #d35400); }
        .severity-card.medium { background: linear-gradient(135deg, #f39c12, #f1c40f); }
        .severity-card.low { background: linear-gradient(135deg, #3498db, #2980b9); }

        .severity-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .severity-count {
            font-size: 2.5em;
            font-weight: bold;
            margin-top: 10px;
        }

        .providers {
            margin-bottom: 30px;
        }

        .providers h2 {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
        }

        .provider-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .provider-card h3 {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #667eea;
        }

        .provider-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .stat {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .stat-label {
            font-weight: 600;
            color: #7f8c8d;
        }

        .critical-text { color: #e74c3c; font-weight: bold; }
        .high-text { color: #e67e22; font-weight: bold; }
        .medium-text { color: #f39c12; font-weight: bold; }
        .low-text { color: #3498db; font-weight: bold; }

        .scanner-results {
            margin-top: 20px;
        }

        .scanner-section {
            margin-bottom: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .scanner-section h4 {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #2c3e50;
        }

        .findings-summary {
            margin-bottom: 15px;
            font-weight: 600;
            color: #7f8c8d;
        }

        .findings-table {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .finding-row {
            display: flex;
            gap: 15px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #ddd;
        }

        .severity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            text-transform: uppercase;
            min-width: 80px;
            text-align: center;
            color: white;
            align-self: flex-start;
        }

        .severity-badge.critical { background: #e74c3c; }
        .severity-badge.high { background: #e67e22; }
        .severity-badge.medium { background: #f39c12; }
        .severity-badge.low { background: #3498db; }
        .severity-badge.unknown { background: #95a5a6; }

        .finding-details {
            flex: 1;
        }

        .finding-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: #2c3e50;
        }

        .finding-meta {
            font-size: 0.9em;
            color: #7f8c8d;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }

        .finding-description {
            font-size: 0.9em;
            color: #555;
            margin-top: 8px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            line-height: 1.5;
        }

        .finding-remediation {
            font-size: 0.9em;
            color: #2c3e50;
            margin-top: 10px;
            padding: 12px;
            background: #e8f5e9;
            border-left: 3px solid #27ae60;
            border-radius: 4px;
            line-height: 1.5;
        }

        .finding-remediation strong {
            color: #27ae60;
            display: block;
            margin-bottom: 5px;
        }

        .error-message {
            color: #e74c3c;
            padding: 10px;
            background: #ffebee;
            border-radius: 4px;
        }

        .more-findings {
            margin-top: 10px;
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
        }

        footer {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            margin-top: 40px;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }

            .summary-cards {
                grid-template-columns: 1fr;
            }

            .provider-summary {
                flex-direction: column;
                gap: 10px;
            }

            .finding-row {
                flex-direction: column;
                gap: 10px;
            }
        }
        """

    def _get_javascript(self) -> str:
        """Return JavaScript for interactive features"""
        return """
        // Add any interactive features here
        console.log('Cloud Security Report loaded');
        """


def main():
    """Main function for CLI usage"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML report from JSON scan results')
    parser.add_argument('json_file', help='Path to input JSON file')
    parser.add_argument('-o', '--output', help='Path to output HTML file', default=None)

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Generate report
    generator = HTMLReportGenerator()
    try:
        output_file = generator.generate_report(args.json_file, args.output)
        print(f"HTML report generated successfully: {output_file}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
