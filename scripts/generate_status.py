import os
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

username = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
token = os.environ.get("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "profile-readme-generator",
}

if token:
    headers["Authorization"] = f"Bearer {token}"

request = urllib.request.Request(
    f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
    headers=headers,
)

try:
    with urllib.request.urlopen(request) as response:
        repos = json.loads(response.read().decode("utf-8"))
except Exception:
    repos = []

languages = {}
latest_repos = []

for repo in repos:
    if repo.get("fork"):
        continue

    name = repo.get("name", "unknown")
    language = repo.get("language") or "Other"

    latest_repos.append(name)
    languages[language] = languages.get(language, 0) + 1

top_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:4]
latest_repos = latest_repos[:3]

updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

language_text = " · ".join([lang for lang, _ in top_languages]) or "Java · TypeScript · AWS"
repo_text = " · ".join(latest_repos) or "building useful things"

svg = f"""
<svg width="900" height="220" viewBox="0 0 900 220" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{
      font: 700 26px 'Segoe UI', Ubuntu, sans-serif;
      fill: #ffffff;
    }}
    .label {{
      font: 600 14px 'Segoe UI', Ubuntu, sans-serif;
      fill: #8b949e;
      letter-spacing: .08em;
    }}
    .value {{
      font: 500 18px 'Segoe UI', Ubuntu, sans-serif;
      fill: #c9d1d9;
    }}
    .accent {{
      fill: #ff6700;
    }}
    .code {{
      font: 500 15px 'JetBrains Mono', 'Fira Code', monospace;
      fill: #7ee787;
    }}
    .blink {{
      animation: blink 1s infinite;
    }}
    @keyframes blink {{
      0%, 45% {{ opacity: 1; }}
      46%, 100% {{ opacity: 0; }}
    }}
  </style>

  <rect x="1" y="1" width="898" height="218" rx="18" fill="#0d1117" stroke="#30363d" />

  <circle cx="36" cy="32" r="6" fill="#ff5f56"/>
  <circle cx="58" cy="32" r="6" fill="#ffbd2e"/>
  <circle cx="80" cy="32" r="6" fill="#27c93f"/>

  <text x="34" y="78" class="title">Kevin's Dev System</text>
  <text x="34" y="112" class="code">$ build --clean --useful --automated<tspan class="blink">_</tspan></text>

  <text x="34" y="152" class="label">CURRENT STACK SIGNALS</text>
  <text x="34" y="180" class="value">{language_text}</text>

  <text x="470" y="152" class="label">RECENTLY TOUCHED</text>
  <text x="470" y="180" class="value">{repo_text}</text>

  <text x="34" y="205" class="label">UPDATED</text>
  <text x="105" y="205" class="value">{updated_at}</text>

  <rect x="814" y="34" width="52" height="52" rx="14" fill="#161b22" stroke="#30363d"/>
  <path d="M831 62L840 71L854 48" stroke="#ff6700" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
""".strip()

Path("assets").mkdir(exist_ok=True)
Path("assets/system-status.svg").write_text(svg, encoding="utf-8")
