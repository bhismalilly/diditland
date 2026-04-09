from aws_assistant import mcp
from aws_assistant.config import COMPONENTS, ENV_BRANCH_MAP
from aws_assistant.tools.component import check_component


@mcp.tool()
def check_deployment(
    github_repo: str,
    ecr_repository: str,
    environment: str,
) -> str:
    """Check if the latest GitHub commits have been deployed as ECR images.

    Compares GitHub branch HEAD with ECR image tags for both frontend and backend.
    If a component's ECR image doesn't match HEAD, it checks the last commit that
    actually changed that component's files to distinguish between "correctly skipped"
    and "failed to deploy".

    Args:
        github_repo: GitHub repo in owner/name format (e.g. EliLillyCo/DC_Marketplace)
        ecr_repository: ECR repository name (e.g. dc_marketplace)
        environment: One of dev, qa, prd
    """
    env = environment.lower()
    if env not in ENV_BRANCH_MAP:
        return f"❌ Unknown environment: {env}. Use one of: {', '.join(ENV_BRANCH_MAP.keys())}"

    branch = ENV_BRANCH_MAP[env]
    results = []
    results.append(f"=== {env.upper()} ({branch} branch) — {ecr_repository} ===\n")

    for component in COMPONENTS:
        try:
            result = check_component(github_repo, ecr_repository, env, branch, component)
        except Exception as e:
            result = f"{component.upper()}: ❌ ERROR\n  {e}"
        results.append(result)
        results.append("")

    return "\n".join(results)


@mcp.tool()
def check_all_environments(
    github_repo: str,
    ecr_repository: str,
) -> str:
    """Check deployment status across all environments (dev, qa, prd).

    Args:
        github_repo: GitHub repo in owner/name format (e.g. EliLillyCo/DC_Marketplace)
        ecr_repository: ECR repository name (e.g. dc_marketplace)
    """
    results = []
    for env in ENV_BRANCH_MAP:
        results.append(check_deployment(github_repo, ecr_repository, env))
        results.append("─" * 60)
    return "\n".join(results)
