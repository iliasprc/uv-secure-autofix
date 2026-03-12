import argparse
import json
import subprocess
import sys

def main(argv=None):
    parser = argparse.ArgumentParser(description="Scans uv.lock using uv-secure and automatically upgrades vulnerable dependencies using uv lock.")
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)
    
    print("🔍 Scanning uv.lock for vulnerabilities using uv-secure...")
    
    try:
        # Run uv-secure --format json
        result = subprocess.run(
            ["uvx", "uv-secure", "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        report_json = result.stdout
    except Exception as e:
        print(f"Error running uv-secure: {e}", file=sys.stderr)
        return 1
        
    try:
        report = json.loads(report_json)
    except json.JSONDecodeError:
        # If output isn't valid JSON, it might just be the success message
        # or uv-secure failed in an unexpected way.
        if result.returncode == 0:
            print("✅ No vulnerable packages found! You are secure. 🚀")
            return 0
        else:
            print(f"uv-secure failed with exit code {result.returncode}:\n{result.stderr}", file=sys.stderr)
            return result.returncode

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

    if not vuln_packages:
        print("✅ No vulnerable packages found in the report! You are secure. 🚀")
        return 0
        
    print(f"🚨 Vulnerable packages identified: {' '.join(vuln_packages)}")
    print("Attempting targeted upgrades...")
    
    cmd_args = ["uv", "lock"]
    for pkg in vuln_packages:
        cmd_args.extend(["--upgrade-package", pkg])
        
    print(f"⚙️  Running: {' '.join(cmd_args)}")
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError:
        print("⚠️ Failed to run uv lock.", file=sys.stderr)
        return 1
        
    print("----------------------------------------")
    diff_result = subprocess.run(["git", "diff", "--quiet", "uv.lock"])
    if diff_result.returncode != 0:
        print("✅ Fixes applied! Run 'git diff uv.lock' to review the updated versions.")
        return 1
    else:
        print("⚠️  No changes made to uv.lock.")
        print("   The vulnerable packages couldn't be upgraded automatically.")
        print("   Check your pyproject.toml to see if the versions are strictly pinned.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
