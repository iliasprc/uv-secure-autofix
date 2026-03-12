# uv-secure-autofix

A pre-commit hook that automatically fixes vulnerabilities in your `uv.lock` file by leveraging `uv-secure` and `uv lock --upgrade-package`.

## Usage

Add the following to your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/iliasprc/uv-secure-autofix
    rev: v0.1.0 # replace with a valid tag
    hooks:
    -   id: uv-secure-autofix
```

## Requirements
- `uv` installed in your environment.
- `uv-secure` installed (typically run via `uvx uv-secure` automatically by this hook).
