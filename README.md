# uv-secure-autofix

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A [pre-commit](https://pre-commit.com/) hook that automatically detects and fixes security vulnerabilities in your Python dependencies managed by `uv`.

## ✨ What it does

This hook ensures your Python projects remain secure without manual intervention. When you commit changes to `uv.lock` or `pyproject.toml`, the hook:

1. **Scans** your dependencies using `uv-secure` to find known vulnerabilities.
2. **Parses** the vulnerability report to identify the exact packages affected.
3. **Auto-fixes** the vulnerabilities by intelligently running `uv lock --upgrade-package <pkg>` for each vulnerable dependency.
4. **Verifies** the changes. If fixes were applied, the commit fails (standard pre-commit behavior for auto-formatting), allowing you to review the updated `uv.lock` and commit again.

If a package cannot be upgraded automatically (e.g., due to strict version pinning in your `pyproject.toml`), the hook will warn you so you can intervene manually.

## 🚀 Usage

Add the following configuration to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/iliasprc/uv-secure-autofix
    rev: v0.1.1 # Use the latest release tag
    hooks:
      - id: uv-secure-autofix
```

## 📋 Requirements

The only requirement is that you must have [`uv`](https://docs.astral.sh/uv/) installed and available in your system's `PATH`.

*(The hook uses `uvx` to automatically download and run the `uv-secure` scanner, so you don't need to install the scanner manually).*

## 💡 Example Output

When a vulnerability is found and fixed:

```text
Auto-fix uv.lock vulnerabilities.........................................Failed
- hook id: uv-secure-autofix
- exit code: 1

🔍 Scanning uv.lock for vulnerabilities using uv-secure...
🚨 Vulnerable packages identified: requests
Attempting targeted upgrades...
⚙️  Running: uv lock --upgrade-package requests
----------------------------------------
✅ Fixes applied! Run 'git diff uv.lock' to review the updated versions.
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
