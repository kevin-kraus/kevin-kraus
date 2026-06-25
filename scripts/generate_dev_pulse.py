import os
import json
import html
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "kevin-kraus")
TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "kevin-profile-readme",
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def fetch_json(url: str):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def safe_text(value: str, max_len: int = 58) -> str:
    value = html.escape(value or "")
    return value if len(value) <= max_len else value[: max_len - 1] + "…"


def main():
    repos = []
    try:
        repos = fetch_json(
            f"https://api.github.com/users/{USERNAME}/repos?sort=updated&direction=desc&per_page=100"
        )
    except Exception as error:
        print(f"GitHub API fallback: {error}")

    public_repos = [repo for repo in repos if not repo.get("fork")]
    recent = public_repos[:3]

    language_counts = {}
    total_stars = 0
    total_forks = 0

    for repo in public_repos:
        language = repo.get("language") or "Other"
        language_counts[language] = language_counts.get(language, 0) + 1
        total_stars += int(repo.get("stargazers_count") or 0)
        total_forks += int(repo.get("forks_count") or 0)

    top_languages = sorted(language_counts.items(), key=lambda item: item[1], reverse=True)[:4]
    language_text = " · ".join([lang for lang, _ in top_languages]) or "Java · TypeScript · AWS · Automation"

    if recent:
        recent_text = " · ".join([safe_text(repo.get("name", "repo"), 22) for repo in recent])
    else:
        recent_text = "building useful software"

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    repo_count = len(public_repos)
    stars_text = str(total_stars)
    forks_text = str(total_forks)

    svg = f"""
<svg width="1100" height="250" viewBox="0 0 1100 250" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="1100" y2="250" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0D1117"/>
      <stop offset="0.64" stop-color="#10151E"/>
      <stop offset="1" stop-color="#17110B"/>
    </linearGradient>
    <linearGradient id="accent" x1="40" y1="39" x2="1050" y2="218" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FF6700"/>
      <stop offset="1" stop-color="#FFB000"/>
    </linearGradient>
  </defs>

  <style>
    .title {{ font: 800 28px 'Segoe UI', Ubuntu, sans-serif; fill: #ffffff; }}
    .subtitle {{ font: 500 15px 'JetBrains Mono', 'Fira Code', monospace; fill: #7ee787; }}
    .label {{ font: 700 12px 'Segoe UI', Ubuntu, sans-serif; fill: #8b949e; letter-spacing: .12em; }}
    .value {{ font: 700 23px 'Segoe UI', Ubuntu, sans-serif; fill: #c9d1d9; }}
    .small {{ font: 500 14px 'Segoe UI', Ubuntu, sans-serif; fill: #8b949e; }}
    .orange {{ fill: #ff8a2a; }}
  </style>

  <rect x="1" y="1" width="1098" height="248" rx="22" fill="url(#card)" stroke="#30363d"/>
  <circle cx="36" cy="34" r="6" fill="#ff5f56"/>
  <circle cx="58" cy="34" r="6" fill="#ffbd2e"/>
  <circle cx="80" cy="34" r="6" fill="#27c93f"/>

  <path d="M40 216 C205 126, 334 239, 488 158 S746 98, 884 171 S1012 221, 1060 167" stroke="url(#accent)" stroke-width="3" opacity=".45"/>

  <text x="40" y="82" class="title">Kevin's Dev Pulse</text>
  <text x="40" y="114" class="subtitle">$ ship --clean --useful --automated</text>

  <g transform="translate(40, 145)">
    <rect width="195" height="66" rx="16" fill="#161b22" stroke="#30363d"/>
    <text x="18" y="24" class="label">PUBLIC REPOS</text>
    <text x="18" y="52" class="value">{repo_count}</text>
  </g>

  <g transform="translate(255, 145)">
    <rect width="195" height="66" rx="16" fill="#161b22" stroke="#30363d"/>
    <text x="18" y="24" class="label">STARS</text>
    <text x="18" y="52" class="value">{stars_text}</text>
  </g>

  <g transform="translate(470, 145)">
    <rect width="195" height="66" rx="16" fill="#161b22" stroke="#30363d"/>
    <text x="18" y="24" class="label">FORKS</text>
    <text x="18" y="52" class="value">{forks_text}</text>
  </g>

  <g transform="translate(700, 70)">
    <text x="0" y="0" class="label">STACK SIGNALS</text>
    <text x="0" y="31" class="value">{safe_text(language_text, 48)}</text>

    <text x="0" y="78" class="label">RECENTLY TOUCHED</text>
    <text x="0" y="109" class="value">{safe_text(recent_text, 42)}</text>

    <text x="0" y="153" class="small">Updated {updated_at}</text>
  </g>

  <rect x="1006" y="34" width="54" height="54" rx="16" fill="#161b22" stroke="#30363d"/>
  <path d="M1022 62L1032 72L1046 49" stroke="#FF8A2A" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""".strip()

    Path("assets").mkdir(exist_ok=True)
    Path("assets/dev-pulse.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
