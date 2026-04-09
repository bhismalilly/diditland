import json

from diditland.utils import run_cmd


def get_ecr_latest_image(ecr_repo: str, env: str, component: str) -> dict | None:
    tag_prefix = f"{env}-{component}-sha-"
    latest_tag = f"{tag_prefix}latest"

    try:
        raw = run_cmd([
            "aws", "ecr", "describe-images",
            "--repository-name", ecr_repo,
            "--no-cli-pager",
            "--image-ids", f"imageTag={latest_tag}",
            "--output", "json",
        ])
    except RuntimeError:
        return None

    data = json.loads(raw)
    images = data.get("imageDetails", [])
    if not images:
        return None

    img = images[0]
    tags = img.get("imageTags", [])
    sha = None
    for t in tags:
        if t.startswith(tag_prefix) and t != latest_tag and len(t) == len(tag_prefix) + 7:
            sha = t[len(tag_prefix):]
            break
    return {
        "short_sha": sha,
        "tags": tags,
        "pushed_at": img.get("imagePushedAt"),
    }
