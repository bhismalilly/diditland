import json

from diditland.utils import run_cmd


def get_branch_head(repo: str, branch: str) -> dict:
    raw = run_cmd(["gh", "api", f"repos/{repo}/commits/{branch}"])
    data = json.loads(raw)
    return {
        "sha": data["sha"],
        "short_sha": data["sha"][:7],
        "message": data["commit"]["message"].split("\n")[0],
        "author": data["commit"]["author"]["name"],
        "date": data["commit"]["author"]["date"],
    }


def get_ecr_commit_info(repo: str, ecr_sha: str) -> dict | None:
    """Look up a commit by its short SHA to get its message and date."""
    try:
        raw = run_cmd(["gh", "api", f"repos/{repo}/commits/{ecr_sha}"])
        data = json.loads(raw)
        return {
            "sha": data["sha"],
            "short_sha": data["sha"][:7],
            "message": data["commit"]["message"].split("\n")[0],
            "author": data["commit"]["author"]["name"],
            "date": data["commit"]["author"]["date"],
        }
    except RuntimeError:
        return None


def is_ancestor(repo: str, commit_sha: str, branch: str) -> bool:
    """Check if a commit is an ancestor of (i.e. exists on) the given branch."""
    try:
        raw = run_cmd([
            "gh", "api",
            f"repos/{repo}/compare/{commit_sha}...{branch}",
            "--jq", ".status",
        ])
        return raw.strip() in ("ahead", "identical")
    except RuntimeError:
        return False


def get_commits_between(repo: str, base_sha: str, branch: str) -> list[dict]:
    """Get commits between base_sha and branch HEAD."""
    try:
        raw = run_cmd([
            "gh", "api",
            f"repos/{repo}/compare/{base_sha}...{branch}",
            "--jq", "[.commits[] | {sha: .sha, message: .commit.message, date: .commit.author.date}]",
        ])
        return json.loads(raw)
    except (RuntimeError, json.JSONDecodeError):
        return []


def find_component_changes(repo: str, base_sha: str, branch: str, component: str) -> list[dict]:
    """Check commits between base_sha and branch HEAD for changes in a component folder.

    Returns list of commits that touched files in the component directory.
    """
    commits = get_commits_between(repo, base_sha, branch)
    touching = []
    for c in commits:
        try:
            raw = run_cmd(["gh", "api", f"repos/{repo}/commits/{c['sha']}", "--jq", "[.files[].filename]"])
            files = json.loads(raw)
            component_files = [f for f in files if f.startswith(f"{component}/")]
            if component_files:
                touching.append({
                    "short_sha": c["sha"][:7],
                    "message": c["message"].split("\n")[0],
                    "date": c["date"],
                    "files": component_files,
                })
        except (RuntimeError, json.JSONDecodeError):
            continue
    return touching
