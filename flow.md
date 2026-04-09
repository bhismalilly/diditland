# ECR Deployment Checker — MCP Tool

## Purpose

An MCP tool for Claude Desktop that checks whether the latest GitHub merge/commit has been picked up and deployed as an ECR image.

## Prerequisites

- AWS CLI v2 (authenticated)
- GitHub CLI (`gh`, authenticated)
- Python 3.x
- `mcp` Python package

## Flow

1. **User calls the tool** from Claude Desktop with:
   - `github_repo` (e.g. `org/repo-name`)
   - `ecr_repository` (ECR repo name)
   - `branch` (default: `main`)
   - `aws_region` (default: `us-east-1`)

2. **Tool fetches latest commit from GitHub:**
   - Runs: `gh api repos/{owner}/{repo}/commits/{branch}`
   - Extracts: commit SHA, author, message, timestamp

3. **Tool fetches recent ECR images:**
   - Runs: `aws ecr describe-images --repository-name {ecr_repo} --region {region}`
   - Extracts: image tags, push timestamps, digests

4. **Tool compares:**
   - Checks if commit SHA exists as an ECR image tag
   - If not, compares timestamps (last commit vs latest image push)

5. **Tool returns:**
   - Latest commit SHA, message, author, time
   - Latest ECR image tag(s), push time
   - **Status:** `DEPLOYED` / `NOT DEPLOYED` / `UNKNOWN`
   - If not deployed: time since commit was made

## File Structure

```
AWS assistant/
├── server.py          # MCP server
├── requirements.txt   # pip dependencies
└── flow.md            # This document
```

## Claude Desktop Config

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-assistant": {
      "command": "python",
      "args": ["<path-to>/server.py"]
    }
  }
}
```
