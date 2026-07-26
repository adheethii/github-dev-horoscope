# 🔮 GitHub Developer Horoscope

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-grey?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

> A CLI tool that reads someone's **real** GitHub activity — languages, commit timing, streaks, repo count — and generates a playful "developer horoscope" from it. The humor comes from real data, not generic zodiac filler.

```
$ python horoscope.py adheethii

🔮 Consulting the commit graphs of adheethii...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Your Developer Horoscope ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sign: The Nocturnal Committer 🌙
(87% of your commits land after 9 PM — the universe suspects
you and your keyboard have an understanding your bed does not.)

Today's Fortune:
With 14 public repos and a commit streak that refuses to quit,
the stars say: ship the thing. Whatever it is. Ship it.

Lucky Language: Python 🐍
Unlucky Habit: 6 repos with zero commits since creation.
               They are not "in progress." They are resting.

Compatibility: Highly compatible with README.md files,
               mildly allergic to writing tests.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Why I Built This

Every "GitHub Wrapped"-style tool I found either needed a paid API key,
an OAuth app, or gave the same three generic insights to everyone
("You love Python!"). I wanted something that:

- Uses only GitHub's free public REST API (no auth needed for public data)
- Runs entirely locally via Ollama — no OpenAI cost, no data leaving my machine
- Grounds every joke in an ACTUAL number from that specific profile,
  so two different users never get the same horoscope

---

## How It Works

```
GitHub username
      ↓
GitHub REST API (public, no auth) — fetch repos, commit activity
      ↓
Compute real stats:
  - top languages, repo count, commit-hour distribution
  - longest streak, most/least active repos
      ↓
Format stats into a prompt with FEW-SHOT examples of the tone wanted
      ↓
Local LLM (Ollama) generates the horoscope FROM those real numbers
      ↓
Rendered to terminal with a bit of ASCII flair
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed, with a model pulled

### Installation

```bash
git clone https://github.com/adheethii/github-dev-horoscope.git
cd github-dev-horoscope

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt

ollama pull llama3.2:1b
```

### Usage

```bash
python horoscope.py <github-username>

# Examples
python horoscope.py adheethii
python horoscope.py torvalds
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| GitHub data | GitHub REST API v3 (public, unauthenticated) |
| LLM | Ollama (llama3.2:1b) — fully local |
| HTTP | `requests` |
| CLI formatting | plain ANSI color codes, no heavy dependency |

---

## Rate Limits

GitHub's unauthenticated REST API allows 60 requests/hour per IP —
plenty for personal use. If you hit the limit, wait an hour or set
a `GITHUB_TOKEN` environment variable for a higher authenticated limit.

## Project Structure

```
github-dev-horoscope/
├── horoscope.py       ← CLI entry point
├── github_stats.py    ← fetches and computes real GitHub stats
├── generator.py       ← builds the prompt and calls Ollama
├── requirements.txt
└── README.md
```
