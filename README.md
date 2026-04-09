# diditland

diditland is a Python MCP server that answers one operational question quickly:

"Did the code on my branch actually land in ECR?"

It compares GitHub branch commits with ECR image tags and reports deployment status per component.

## Core capabilities

- Checks deployment status for `frontend` and `backend` independently.
- Supports environment to branch mapping:
  - `dev -> dev`
  - `qa -> qa`
  - `prd -> main`
- Detects real deployment drift vs intentional pipeline skip (path-filtered checks).
- Exposes MCP tools that work from Claude Desktop (or any MCP-compatible client).

## How comparison works

For each component (`frontend`, `backend`) and environment (`dev`, `qa`, `prd`):

1. Fetch branch HEAD commit from GitHub.
2. Resolve ECR tag `<env>-<component>-sha-latest`.
3. Extract short SHA from sibling tag pattern `<env>-<component>-sha-<7charsha>`.
4. Compare ECR short SHA to branch HEAD short SHA.
5. If not equal, check whether the ECR commit is on the target branch and whether relevant files changed since that commit.

This lets the tool distinguish:

- deployed
- not deployed
- correctly skipped because component files did not change

## ECR tag convention required

diditland expects these tags to exist on the same image:

- `<env>-frontend-sha-latest`
- `<env>-frontend-sha-<7charsha>`
- `<env>-backend-sha-latest`
- `<env>-backend-sha-<7charsha>`

If this convention is missing, results may show "No ECR image found" or "Not deployed".

## Prerequisites

- Python 3.10+
- AWS credentials with permission to read ECR images
- GitHub CLI installed and authenticated (`gh auth login`)
- Access to target GitHub repo and ECR repository
- Optional but recommended: `uv`

## Install

### Option 1: Install as a tool (recommended)

```bash
uv tool install git+https://github.com/bhismalilly/diditland
```

### Option 2: Run from local clone

```bash
uv sync
uv run python server.py
```

## Configure Claude Desktop

Edit `claude_desktop_config.json` and add one of the following.

### If installed with `uv tool install`

```json
{
  "mcpServers": {
    "diditland": {
      "command": "diditland"
    }
  }
}
```

### If running from local project

```json
{
  "mcpServers": {
    "diditland": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "<absolute-path-to-AWS assistant>"
    }
  }
}
```

Restart Claude Desktop after saving config.

## MCP tools

### `check_deployment(github_repo, ecr_repository, environment)`

Checks one environment (`dev`, `qa`, or `prd`) for both components.

Inputs:

- `github_repo`: `owner/repo` (example: `EliLillyCo/DC_Marketplace`)
- `ecr_repository`: ECR repository name
- `environment`: `dev` | `qa` | `prd`

### `check_all_environments(github_repo, ecr_repository)`

Runs `check_deployment` for `dev`, `qa`, and `prd`.

### `check_last_component_change(github_repo, ecr_repository, environment, component)`

Shows component-level commit/file changes since the last ECR image.

Inputs:

- `component`: `frontend` | `backend`

## Interpreting results

- `DEPLOYED`: ECR image matches branch HEAD for that component.
- `DEPLOYED (path-filtered)`: ECR SHA is older than HEAD, but no files in that component changed.
- `NOT DEPLOYED`: Component changed since ECR SHA, or ECR commit is not on target branch.
- `NO ECR IMAGE FOUND`: `<env>-<component>-sha-latest` tag not found.

## Configuration constants

Current defaults in code:

- AWS region: `us-east-2`
- components: `frontend`, `backend`
- env map: `dev -> dev`, `qa -> qa`, `prd -> main`

See `diditland/config.py` to adjust.

## Local development

```bash
uv sync
uv run python server.py
```

Entry point:

- `server.py` calls `diditland.main()`
- MCP transport is `stdio`

## Project layout

```text
.
|-- server.py
|-- pyproject.toml
|-- README.md
`-- diditland/
    |-- __init__.py
    |-- config.py
    |-- utils.py
    |-- services/
    |   |-- github.py
    |   `-- ecr.py
    `-- tools/
        |-- deployment.py
        `-- component.py
```

## Troubleshooting

- GitHub auth fails:
  - run `gh auth status`
  - if needed, run `gh auth login`
- ECR image not found:
  - verify repository name and tag convention
  - confirm AWS account/region and IAM permissions
- Wrong deployment result:
  - check env to branch mapping in `diditland/config.py`
  - confirm component directories are named `frontend/` and `backend/` in the GitHub repo

## License

Add your project license here (for example: MIT).
