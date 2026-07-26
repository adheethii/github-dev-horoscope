"""
Fetches and computes real GitHub statistics for a given username,
using only GitHub's free, unauthenticated public REST API.
"""

import requests
from collections import Counter
from datetime import datetime, timezone


GITHUB_API = "https://api.github.com"


class GitHubStatsError(Exception):
    """Raised when the requested user/data can't be fetched."""


def fetch_user_stats(username: str) -> dict:
    """
    Fetches public repos and commit activity for a user, and
    computes a handful of real, specific stats to ground the
    horoscope in actual data rather than generic filler.
    """
    user_resp = requests.get(f"{GITHUB_API}/users/{username}", timeout=10)
    if user_resp.status_code == 404:
        raise GitHubStatsError(f"No GitHub user found named '{username}'.")
    user_resp.raise_for_status()
    user_data = user_resp.json()

    repos_resp = requests.get(
        f"{GITHUB_API}/users/{username}/repos",
        params={"per_page": 100, "sort": "updated"},
        timeout=10,
    )
    repos_resp.raise_for_status()
    repos = repos_resp.json()

    if not isinstance(repos, list):
        raise GitHubStatsError(f"Unexpected response fetching repos for '{username}'.")

    language_counts = Counter()
    empty_repos = []
    most_recent_repo = None
    most_recent_time = None

    for repo in repos:
        if repo.get("fork"):
            continue  # skip forks — we want original work

        lang = repo.get("language")
        if lang:
            language_counts[lang] += 1

        pushed_at = repo.get("pushed_at")
        created_at = repo.get("created_at")

        if pushed_at and created_at and pushed_at == created_at:
            # Never pushed to since creation — a genuinely "resting" repo
            empty_repos.append(repo["name"])

        if pushed_at:
            pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            if most_recent_time is None or pushed_dt > most_recent_time:
                most_recent_time = pushed_dt
                most_recent_repo = repo["name"]

    top_languages = language_counts.most_common(3)

    commit_hours = _fetch_recent_commit_hours(username, repos[:5])
    night_owl_pct = _compute_night_owl_percentage(commit_hours)

    return {
        "username": username,
        "public_repos": user_data.get("public_repos", len(repos)),
        "followers": user_data.get("followers", 0),
        "account_created": user_data.get("created_at", "unknown"),
        "top_languages": top_languages,
        "empty_repos": empty_repos,
        "most_recent_repo": most_recent_repo,
        "total_commit_samples": len(commit_hours),
        "night_owl_pct": night_owl_pct,
    }


def _fetch_recent_commit_hours(username: str, repos: list) -> list:
    """
    Samples commit timestamps from a few of the user's most
    recently-updated repos, to estimate what hours they tend
    to commit at. Kept small (few repos, few commits each) to
    stay comfortably within the unauthenticated rate limit.
    """
    hours = []

    for repo in repos:
        if repo.get("fork"):
            continue
        repo_name = repo.get("name")
        if not repo_name:
            continue

        try:
            resp = requests.get(
                f"{GITHUB_API}/repos/{username}/{repo_name}/commits",
                params={"per_page": 10},
                timeout=10,
            )
            if resp.status_code != 200:
                continue

            for commit in resp.json():
                date_str = commit.get("commit", {}).get("author", {}).get("date")
                if date_str:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    hours.append(dt.hour)

        except (requests.RequestException, ValueError, KeyError):
            continue  # a single repo failing shouldn't break the whole run

    return hours


def _compute_night_owl_percentage(hours: list) -> float:
    """% of sampled commits made between 9 PM and 4 AM (UTC)."""
    if not hours:
        return 0.0

    night_commits = sum(1 for h in hours if h >= 21 or h < 4)
    return round((night_commits / len(hours)) * 100, 1)
