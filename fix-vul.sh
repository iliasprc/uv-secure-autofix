#!/usr/bin/env bash
# Exit immediately if a command (other than uv-secure) fails
set -e

echo "🔍 Scanning uv.lock for vulnerabilities using uv-secure..."

# 1. Create a temporary file for the JSON output
REPORT_FILE=$(mktemp)

echo "⚡ Running uv-secure and saving report to $REPORT_FILE..."
# Run uv-secure. We use '|| true' because finding a vulnerability returns a non-zero 
# exit status, and we don't want the script to crash before fixing it.
uvx uv-secure --format json > "$REPORT_FILE" || true

# 2. Parse JSON using Python to get a space-separated list of vulnerable packages
VULN_PACKAGES=$(python3 -c "
import json, sys

try:
    with open('$REPORT_FILE') as f:
        report = json.load(f)
except Exception:
    sys.exit(0)

vuln_packages = set()

# Handle different possible JSON schemas from uv-secure
if isinstance(report, list):
    for item in report:
        if 'name' in item: vuln_packages.add(item['name'])
        elif 'package' in item: vuln_packages.add(item['package'])
elif isinstance(report, dict):
    if 'vulnerabilities' in report:
        for vuln in report['vulnerabilities']:
            pkg = vuln.get('package_name') or vuln.get('package') or vuln.get('name')
            if pkg: vuln_packages.add(pkg)
    if 'files' in report:
        for file_info in report.get('files', []):
            for dep in file_info.get('dependencies', []):
                if dep.get('vulns'):
                    vuln_packages.add(dep.get('name'))

# Print as space-separated string for Bash
if vuln_packages:
    print(' '.join(vuln_packages))
")

# Clean up the temporary file
rm "$REPORT_FILE"

# 3. Check if any vulnerable packages were actually returned
if [ -z "$VULN_PACKAGES" ]; then
    echo "✅ No vulnerable packages found in the report! You are secure. 🚀"
    exit 0
fi

echo "🚨 Vulnerable packages identified: $VULN_PACKAGES"
echo "Attempting targeted upgrades..."

# 4. Build the upgrade command safely using a Bash array
CMD_ARGS=("lock")
for pkg in $VULN_PACKAGES; do
    CMD_ARGS+=("--upgrade-package" "$pkg")
done

echo "⚙️  Running: uv ${CMD_ARGS[@]}"
uv "${CMD_ARGS[@]}"

# 5. Verify the results
echo "----------------------------------------"
if ! git diff --quiet uv.lock; then
    echo "✅ Fixes applied! Run 'git diff uv.lock' to review the updated versions."
    exit 1
else
    echo "⚠️  No changes made to uv.lock."
    echo "   The vulnerable packages couldn't be upgraded automatically."
    echo "   Check your pyproject.toml to see if the versions are strictly pinned."
fi
