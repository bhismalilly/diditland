import boto3
from botocore.exceptions import ClientError

from diditland.config import AWS_REGION

_ecr_client = boto3.client("ecr", region_name=AWS_REGION)


def get_ecr_latest_image(ecr_repo: str, env: str, component: str) -> dict | None:
    tag_prefix = f"{env}-{component}-sha-"
    latest_tag = f"{tag_prefix}latest"

    try:
        resp = _ecr_client.describe_images(
            repositoryName=ecr_repo,
            imageIds=[{"imageTag": latest_tag}],
        )
    except (ClientError, Exception):
        return None

    images = resp.get("imageDetails", [])
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
        "pushed_at": str(img.get("imagePushedAt", "")),
    }
