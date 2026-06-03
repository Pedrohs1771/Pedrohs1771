from __future__ import annotations

from datetime import datetime, timezone
import os
import urllib.request
import json

USERNAME = "Pedrohs1771"
README = "README.md"


def fetch_public_repos() -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=6",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Pedrohs1771-profile-pulse",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def build_block() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    repos = [
        repo for repo in fetch_public_repos()
        if repo.get("name", "").lower() != USERNAME.lower()
    ]
    lines = [
        "<!-- pulse:start -->",
        f"**Last profile sync:** `{now}`",
        "",
        "| Active signal | Repository | Stack |",
        "|---|---|---|",
    ]
    for repo in repos[:4]:
        name = repo.get("name", "unknown")
        url = repo.get("html_url", "#")
        language = repo.get("language") or "mixed"
        description = (repo.get("description") or "no public description").replace("|", "/")
        if len(description) > 96:
            description = description[:93].rstrip() + "..."
        lines.append(f"| `{language}` | [{name}]({url}) | {description} |")
    lines.append("<!-- pulse:end -->")
    return "\n".join(lines)


def main() -> int:
    with open(README, "r", encoding="utf-8") as file:
        readme = file.read()

    start = "<!-- pulse:start -->"
    end = "<!-- pulse:end -->"
    if start not in readme or end not in readme:
        raise SystemExit("pulse markers not found")

    before = readme.split(start, 1)[0]
    after = readme.split(end, 1)[1]
    updated = before + build_block() + after

    with open(README, "w", encoding="utf-8", newline="\n") as file:
        file.write(updated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
