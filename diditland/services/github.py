import subprocess

import requests

_token = None
_session = None


def _get_session() -> requests.Session:
    global _token, _session
    if _session is None:
        _token = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        _session = requests.Session()
        _session.headers.update({
            "Authorization": f"Bearer {_token}",
            "Accept": "application/vnd.github+json",
        })
    return _session


def _gh_api(endpoint: str) -> dict | list:
    resp = _get_session().get(f"https://api.github.com/{endpoint}", timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_branch_head(repo: str, branch: str) -> dict:
    data = _gh_api(f"repos/{repo}/commits/{branch}")
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
        data = _gh_api(f"repos/{repo}/commits/{ecr_sha}")
        return {
            "sha": data["sha"],
            "short_sha": data["sha"][:7],
            "message": data["commit"]["message"].split("\n")[0],
            "author": data["commit"]["author"]["name"],
            "date": data["commit"]["author"]["date"],
        }
    except Exception:
        return None


def is_ancestor(repo: str, commit_sha: str, branch: str) -> bool:
    """Check if a commit is an ancestor of (i.e. exists on) the given branch."""
    try:
        data = _gh_api(f"repos/{repo}/compare/{commit_sha}...{branch}")
        return data.get("status") in ("ahead", "identical")
    except Exception:
        return False


def get_commits_between(repo: str, base_sha: str, branch: str) -> list[dict]:
    """Get commits between base_sha and branch HEAD."""
    try:
        data = _gh_api(f"repos/{repo}/compare/{base_sha}...{branch}")
        return [
            {"sha": c["sha"], "message": c["commit"]["message"], "date": c["commit"]["author"]["date"]}
            for c in data.get("commits", [])
        ]
    except Exception:
        return []


def find_component_changes(repo: str, base_sha: str, branch: str, component: str) -> list[dict]:
    """Check commits between base_sha and branch HEAD for changes in a component folder.

    Returns list of commits that touched files in the component directory.
    """
    commits = get_commits_between(repo, base_sha, branch)
    touching = []
    for c in commits:
        try:
            data = _gh_api(f"repos/{repo}/commits/{c['sha']}")
            files = [f["filename"] for f in data.get("files", [])]
            component_files = [f for f in files if f.startswith(f"{component}/")]
            if component_files:
                touching.append({
                    "short_sha": c["sha"][:7],
                    "message": c["message"].split("\n")[0],
                    "date": c["date"],
                    "files": component_files,
                })
        except Exception:
            continue
    return touching
