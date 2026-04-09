# diditland

> "Did it land?" — an MCP server that checks whether your GitHub commits actually made it to ECR.

Compares branch HEAD with ECR image tags to detect deployment drift across environments.

## What it does

- Compares GitHub branch HEAD with ECR `*-sha-latest` image tags
- Checks both **frontend** and **backend** components
- Distinguishes between "failed to deploy" and "correctly skipped" using path-filtered analysis
- Supports **dev**, **qa**, and **prd** environments (mapped to `dev`, `qa`, `main` branches)

## Tools

| Tool | Description |
|------|-------------|
| `check_deployment` | Check if latest commits are deployed for a single environment |
| `check_all_environments` | Check deployment status across dev, qa, and prd |
| `check_last_component_change` | Drill into what changed in frontend or backend since the last ECR image |

## Prerequisites

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) (authenticated)
- [GitHub CLI](https://cli.github.com/) (`gh`, authenticated)
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv tool install git+https://github.com/bhismalilly/diditland
```

## Configure Claude Desktop

Open `claude_desktop_config.json`:

- **Windows:** `Ctrl ,` → Developer → Edit Config
- **macOS:** `⌘ ,` → Developer → Edit Config

Add:

```json
{
  "mcpServers": {
    "diditland": {
      "command": "diditland"
    }
  }
}
```

Restart Claude Desktop.

## Example usage

> "Check if DC_Marketplace is deployed in dev"

The tool will compare the `dev` branch HEAD with ECR images tagged `dev-frontend-sha-latest` and `dev-backend-sha-latest`, and report the status for each component.

## Project structure

```
├── server.py                  # Entry point (python server.py)
├── pyproject.toml
└── diditland/
    ├── __init__.py            # FastMCP instance + tool registration
    ├── config.py              # Environment/branch mappings, component list
    ├── utils.py               # run_cmd(), time_ago()
    ├── services/
    │   ├── github.py          # GitHub API interactions
    │   └── ecr.py             # AWS ECR image lookups
    └── tools/
        ├── deployment.py      # check_deployment, check_all_environments
        └── component.py       # check_component, check_last_component_change
```
