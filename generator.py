"""
Builds a prompt grounded in a user's REAL GitHub stats, and calls
a local Ollama model to generate the horoscope text.
"""

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:1b"


PROMPT_TEMPLATE = """You are a witty astrologer who ONLY reads GitHub commit
graphs instead of star charts. Write a short, funny "developer horoscope"
for this specific person, using ONLY the real facts given below. Every
joke must reference one of these actual numbers or names — do not invent
generic zodiac content that could apply to anyone.

Real facts about this GitHub user:
- Username: {username}
- Public repos: {public_repos}
- Followers: {followers}
- Top languages used: {top_languages}
- Most recently active repo: {most_recent_repo}
- Repos with zero commits since creation ("resting" repos): {empty_repos}
- Percentage of sampled commits made late at night (9pm-4am): {night_owl_pct}%

Style examples (tone to match, NOT content to copy):
---
Example 1:
"Sign: The Nocturnal Committer. 87% of your commits land after 9 PM —
the universe suspects you and your keyboard have an understanding your
bed does not."

Example 2:
"Lucky Language: Python. Unlucky Habit: 6 repos with zero commits since
creation. They are not 'in progress.' They are resting."
---

Now write a horoscope for {username} with these sections:
1. A one-line "Sign" (a made-up, GitHub-flavored astrological sign name)
2. "Today's Fortune" — 1-2 sentences
3. "Lucky Language" and "Unlucky Habit" — grounded in their actual data
4. "Compatibility" — one playful sentence

Keep the whole thing under 120 words. Be affectionate, not mean.
If a stat is missing or zero (e.g. no empty repos), skip that joke
gracefully rather than inventing one."""


class HoroscopeGenerationError(Exception):
    """Raised when the local Ollama call fails."""


def generate_horoscope(stats: dict, model: str = DEFAULT_MODEL) -> str:
    top_languages_str = ", ".join(
        f"{lang} ({count} repos)" for lang, count in stats.get("top_languages", [])
    ) or "no dominant language detected"

    empty_repos_str = (
        ", ".join(stats.get("empty_repos", [])[:3]) or "none — every repo has commits"
    )

    prompt = PROMPT_TEMPLATE.format(
        username=stats["username"],
        public_repos=stats["public_repos"],
        followers=stats["followers"],
        top_languages=top_languages_str,
        most_recent_repo=stats.get("most_recent_repo") or "unknown",
        empty_repos=empty_repos_str,
        night_owl_pct=stats.get("night_owl_pct", 0),
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise HoroscopeGenerationError(
            f"Could not reach Ollama at {OLLAMA_URL}. "
            f"Is 'ollama serve' running, and is '{model}' pulled? "
            f"Original error: {e}"
        ) from e

    data = response.json()
    horoscope_text = data.get("response", "").strip()

    if not horoscope_text:
        raise HoroscopeGenerationError("Ollama returned an empty response.")

    return horoscope_text
