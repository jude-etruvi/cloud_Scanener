#!/bin/bash
# Daily Security Scan Script
# Schedule this with cron for automated daily scans

# Configuration
SCANNER_DIR="/path/to/cloud_security_scanner"
OUTPUT_DIR="$SCANNER_DIR/reports/daily"
LOG_FILE="$SCANNER_DIR/logs/daily_scan.log"
ALERT_EMAIL="security-team@example.com"

# Create output directory
mkdir -p "$OUTPUT_DIR/$(date +%Y%m%d)"

# Activate virtual environment if exists
if [ -d "$SCANNER_DIR/venv" ]; then
    source "$SCANNER_DIR/venv/bin/activate"
fi

# Change to scanner directory
cd "$SCANNER_DIR"

# Run scan
echo "Starting daily security scan at $(date)" >> "$LOG_FILE"

python scanner.py \
    --provider all \
    --output-dir "$OUTPUT_DIR/$(date +%Y%m%d)" \
    --verbose \
    2>&1 | tee -a "$LOG_FILE"

SCAN_EXIT_CODE=$?

# Check results
if [ $SCAN_EXIT_CODE -eq 0 ]; then
    echo "Scan completed successfully - no critical/high issues found" >> "$LOG_FILE"
    STATUS="SUCCESS"
else
    echo "Scan found critical/high issues - review required" >> "$LOG_FILE"
    STATUS="ALERT"
fi

# Send notification (optional - requires mail/sendmail)
if command -v mail &> /dev/null; then
    if [ "$STATUS" == "ALERT" ]; then
        echo "Daily security scan found critical or high severity issues. Please review the reports at $OUTPUT_DIR/$(date +%Y%m%d)" | \
            mail -s "ALERT: Security Scan Findings" "$ALERT_EMAIL"
    fi
fi

# Clean up old reports (keep last 30 days)
find "$OUTPUT_DIR" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

echo "Daily scan completed at $(date)" >> "$LOG_FILE"

exit $SCAN_EXIT_CODE
