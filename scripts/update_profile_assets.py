import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


USERNAME = "huizhang557"
PROJECT = "ai-watch"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "readme"


def get_json(url):
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-profile-assets",
            "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def text(value):
    return html.escape(str(value), quote=True)


def write_asset(name, content):
    (OUTPUT / name).write_text(content, encoding="utf-8")


def main():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    repos = get_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=all")
    project = get_json(f"https://api.github.com/repos/{USERNAME}/{PROJECT}")

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    languages = {}
    for repo in repos:
        repo_languages = get_json(repo["languages_url"])
        for language, amount in repo_languages.items():
            languages[language] = languages.get(language, 0) + amount
    top_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:5]
    language_total = sum(amount for _, amount in top_languages) or 1

    write_asset(
        "hero.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-labelledby="title desc">
  <title id="title">{text(user.get("name") or USERNAME)} GitHub profile</title>
  <desc id="desc">C++ and Qt developer profile banner generated from GitHub data.</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#FDF8F4"/><stop offset="100%" stop-color="#F7F3EE"/></linearGradient><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="320" rx="38" fill="url(#bg)"/>
  <g transform="translate(80,94)">
    <text class="sans" font-size="22" font-weight="600" fill="#94AAB9">你好，我是</text>
    <text class="sans" y="72" font-size="64" font-weight="750" fill="#3C4F66">{text(user.get("name") or USERNAME)}</text>
    <text class="sans" y="126" font-size="28" fill="#6F7F90">C++ / Qt 开发者</text>
  </g>
  <g transform="translate(810,64)">
    <rect width="340" height="180" rx="26" fill="#FFFFFF" stroke="#E9EDF2" stroke-width="1.5"/>
    <text class="sans" x="30" y="42" font-size="15" font-weight="700" fill="#A9BCC9">GitHub 概览</text>
    <g transform="translate(30,80)"><text class="sans" font-size="38" font-weight="700" fill="#3C4F66">{len(repos)}</text><text class="sans" y="26" font-size="16" fill="#8A9CAD">仓库</text></g>
    <g transform="translate(145,80)"><text class="sans" font-size="38" font-weight="700" fill="#3C4F66">{total_stars}</text><text class="sans" y="26" font-size="16" fill="#8A9CAD">Stars</text></g>
    <g transform="translate(248,80)"><text class="sans" font-size="38" font-weight="700" fill="#3C4F66">{user.get("followers", 0)}</text><text class="sans" y="26" font-size="16" fill="#8A9CAD">关注者</text></g>
  </g>
</svg>
''',
    )

    cards = []
    for label, value in (("公开仓库", len(repos)), ("Stars", total_stars), ("关注者", user.get("followers", 0)), ("正在关注", user.get("following", 0))):
        cards.append(f'<text class="sans" x="30" y="58" font-size="48" font-weight="700" fill="#3C4F66">{value}</text><text class="sans" x="30" y="92" font-size="16" fill="#8A9CAD">{label}</text>')
    card_groups = "".join(f'<g transform="translate({60 + index * 280},44)"><rect width="240" height="120" rx="20" fill="#FFFFFF" stroke="#E9EDF2" stroke-width="1.5"/>{card}</g>' for index, card in enumerate(cards))
    language_rows = []
    for index, (language, amount) in enumerate(top_languages):
        percent = round(amount * 100 / language_total)
        width = max(8, round(720 * percent / 100))
        language_rows.append(f'<g transform="translate(0,{index * 44})"><text x="0" y="20" fill="#6F7F90">{text(language)}</text><rect x="150" y="0" width="720" height="28" rx="6" fill="#E9EDF2"/><rect x="150" y="0" width="{width}" height="28" rx="6" fill="#6F7F90"/><text x="890" y="20" fill="#3C4F66" font-weight="600">{percent}%</text></g>')
    write_asset(
        "stats-overview.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500" role="img" aria-labelledby="title desc">
  <title id="title">{text(user.get("name") or USERNAME)} GitHub overview</title><desc id="desc">GitHub profile statistics generated from the GitHub API.</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs><rect width="1200" height="500" rx="28" fill="#FDF8F4"/>{card_groups}
  <text class="sans" x="60" y="220" font-size="24" font-weight="700" fill="#3C4F66">主要语言</text><g transform="translate(60,270)" class="sans" font-size="18">{"".join(language_rows)}</g>
</svg>
''',
    )

    write_asset(
        "pinned-bbdown.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="220" viewBox="0 0 1200 220" role="img" aria-labelledby="title desc"><title id="title">{text(project["name"])} project card</title><desc id="desc">Generated project card for the user's featured GitHub repository.</desc><defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs><rect width="1200" height="220" rx="30" fill="#FDF8F4" stroke="#E9EDF2" stroke-width="1.5"/><g transform="translate(48,44)"><text class="sans" font-size="44" font-weight="700" fill="#3C4F66">{text(project["name"])}</text><text class="sans" x="0" y="94" font-size="20" fill="#6F7F90">语言：{text(project.get("language") or "未指定")} · {text(project.get("description") or "个人项目实践")}</text></g><g transform="translate(940,64)"><text class="sans" font-size="26" font-weight="700" fill="#3C4F66">{project.get("stargazers_count", 0)}</text><text class="sans" y="26" font-size="14" fill="#8A9CAD">Stars</text><g transform="translate(90,0)"><text class="sans" font-size="26" font-weight="700" fill="#3C4F66">{project.get("forks_count", 0)}</text><text class="sans" y="26" font-size="14" fill="#8A9CAD">Forks</text></g></g></svg>
''',
    )

    write_asset(
        "achievements.svg",
        '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="160" viewBox="0 0 1200 160" role="img" aria-labelledby="title desc"><title id="title">Harry James profile highlights</title><desc id="desc">Profile highlights generated from the user's current projects and technologies.</desc><defs><style>.sans{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}</style></defs><rect width="1200" height="160" rx="28" fill="#FDF8F4"/><g transform="translate(26,48)" class="sans" font-size="18" font-weight="600"><g><rect width="188" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">C++ / Qt</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">主要方向</text></g><g transform="translate(204,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">Python</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">脚本与自动化</text></g><g transform="translate(400,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">AI Watch</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">精选项目</text></g><g transform="translate(596,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">Kotlin</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">项目语言</text></g><g transform="translate(792,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">GitHub</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">持续维护</text></g></g></svg>
''',
    )


if __name__ == "__main__":
    main()