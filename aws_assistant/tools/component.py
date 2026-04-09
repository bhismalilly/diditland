from aws_assistant import mcp
from aws_assistant.config import COMPONENTS, ENV_BRANCH_MAP
from aws_assistant.services.ecr import get_ecr_latest_image
from aws_assistant.services.github import (
    find_component_changes,
    get_branch_head,
    get_ecr_commit_info,
    is_ancestor,
)
from aws_assistant.utils import time_ago


def check_component(repo: str, ecr_repo: str, env: str, branch: str, component: str) -> str:
    lines = []
    header = component.upper()

    ecr = get_ecr_latest_image(ecr_repo, env, component)
    if ecr is None:
        lines.append(f"{header}: ⚠️  NO ECR IMAGE FOUND ({env}-{component}-sha-latest not found)")
        return "\n".join(lines)

    head = get_branch_head(repo, branch)

    # Case 1: ECR matches branch HEAD
    if ecr["short_sha"] == head["short_sha"]:
        lines.append(f"{header}: ✅ DEPLOYED")
        lines.append(f"  Branch HEAD : {head['short_sha']} — \"{head['message']}\" ({time_ago(head['date'])})")
        lines.append(f"  ECR latest  : {ecr['short_sha']} (pushed {ecr['pushed_at']})")
        return "\n".join(lines)

    # Case 2: ECR doesn't match HEAD — check if ECR commit exists on this branch
    ecr_commit = get_ecr_commit_info(repo, ecr["short_sha"])
    on_branch = is_ancestor(repo, ecr["short_sha"], branch) if ecr_commit else False

    if ecr_commit and on_branch:
        # Check if any commits between ECR and HEAD actually changed this component
        changes = find_component_changes(repo, ecr["short_sha"], branch, component)
        if changes:
            lines.append(f"{header}: ❌ NOT DEPLOYED")
            lines.append(f"  Branch HEAD        : {head['short_sha']} — \"{head['message']}\" ({time_ago(head['date'])})")
            lines.append(f"  ECR latest         : {ecr['short_sha']} — \"{ecr_commit['message']}\" ({time_ago(ecr_commit['date'])})")
            lines.append(f"  ⚠️  {len(changes)} commit(s) since ECR image changed {component}:")
            for ch in changes:
                lines.append(f"    • {ch['short_sha']} — \"{ch['message']}\" ({time_ago(ch['date'])})")
                for f in ch["files"][:3]:
                    lines.append(f"      {f}")
                if len(ch["files"]) > 3:
                    lines.append(f"      ... and {len(ch['files']) - 3} more files")
        else:
            lines.append(f"{header}: ✅ DEPLOYED (path-filtered)")
            lines.append(f"  Branch HEAD        : {head['short_sha']} — \"{head['message']}\" ({time_ago(head['date'])})")
            lines.append(f"  ECR latest         : {ecr['short_sha']} — \"{ecr_commit['message']}\" ({time_ago(ecr_commit['date'])})")
            lines.append(f"  → No {component} files changed since ECR image was built")
    else:
        lines.append(f"{header}: ❌ NOT DEPLOYED")
        lines.append(f"  Branch HEAD        : {head['short_sha']} — \"{head['message']}\" ({time_ago(head['date'])})")
        if ecr_commit:
            lines.append(f"  ECR latest         : {ecr['short_sha']} — \"{ecr_commit['message']}\" ({time_ago(ecr_commit['date'])})")
        else:
            lines.append(f"  ECR latest         : {ecr['short_sha']} (pushed {ecr['pushed_at']})")
        lines.append(f"  ⚠️  ECR image commit is not on {branch} branch")

    return "\n".join(lines)


@mcp.tool()
def check_last_component_change(
    github_repo: str,
    ecr_repository: str,
    environment: str,
    component: str,
) -> str:
    """Check what changed in a specific component (frontend/backend) since the last ECR image.

    Fetches all commits between the ECR image SHA and branch HEAD, then filters
    for commits that touched files in the component folder.

    Args:
        github_repo: GitHub repo in owner/name format (e.g. EliLillyCo/DC_Marketplace)
        ecr_repository: ECR repository name (e.g. dc_marketplace)
        environment: One of dev, qa, prd
        component: One of frontend, backend
    """
    env = environment.lower()
    comp = component.lower()
    if env not in ENV_BRANCH_MAP:
        return f"❌ Unknown environment: {env}. Use one of: {', '.join(ENV_BRANCH_MAP.keys())}"
    if comp not in COMPONENTS:
        return f"❌ Unknown component: {comp}. Use one of: {', '.join(COMPONENTS)}"

    branch = ENV_BRANCH_MAP[env]
    ecr = get_ecr_latest_image(ecr_repository, env, comp)
    if ecr is None:
        return f"⚠️  No ECR image found for {env}-{comp}-sha-latest"

    head = get_branch_head(github_repo, branch)
    if ecr["short_sha"] == head["short_sha"]:
        return f"✅ {comp.upper()} ECR image matches branch HEAD ({head['short_sha']}). Nothing to check."

    ecr_commit = get_ecr_commit_info(github_repo, ecr["short_sha"])
    changes = find_component_changes(github_repo, ecr["short_sha"], branch, comp)

    lines = [f"=== {comp.upper()} changes since ECR image ({env.upper()}) ===\n"]
    lines.append(f"Branch HEAD : {head['short_sha']} — \"{head['message']}\"")
    if ecr_commit:
        lines.append(f"ECR image   : {ecr['short_sha']} — \"{ecr_commit['message']}\"")
    else:
        lines.append(f"ECR image   : {ecr['short_sha']} (pushed {ecr['pushed_at']})")
    lines.append("")

    if not changes:
        lines.append(f"✅ No {comp} files changed between ECR image and branch HEAD.")
        lines.append(f"   Pipeline correctly skipped rebuild.")
    else:
        lines.append(f"❌ {len(changes)} commit(s) changed {comp} files since ECR image:\n")
        for ch in changes:
            lines.append(f"  {ch['short_sha']} — \"{ch['message']}\" ({time_ago(ch['date'])})")
            for f in ch["files"]:
                lines.append(f"    {f}")
            lines.append("")

    return "\n".join(lines)
