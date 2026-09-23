import html
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USERNAME = "huizhang556"
DISPLAY_NAME = "Selina Martin"
PROJECT = "vx_data_watch"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "readme"


def get_json(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-assets",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for attempt in range(3):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 403:
                raise RuntimeError(
                    f"GitHub API access was denied or rate-limited for {url}; set GITHUB_TOKEN and retry."
                ) from error
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"GitHub API request failed ({error.code}) for {url}") from error
        except URLError as error:
            if attempt == 2:
                raise RuntimeError(f"GitHub API request could not reach {url}") from error
        time.sleep(2**attempt)


def text(value):
    return html.escape(str(value), quote=True)


def write_asset(name, content):
    (OUTPUT / name).write_text(content, encoding="utf-8")


def get_public_repos():
    repos = []
    page = 1
    while True:
        batch = get_json(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=all&page={page}"
        )
        if not batch:
            break
        repos.extend(repo for repo in batch if not repo.get("private", False))
        if len(batch) < 100:
            break
        page += 1
    return repos


def main():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    repos = get_public_repos()
    project = get_json(f"https://api.github.com/repos/{USERNAME}/{PROJECT}")

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    languages = {}
    for repo in repos:
        try:
            repo_languages = get_json(repo["languages_url"])
        except RuntimeError as error:
            if "denied or rate-limited" in str(error):
                raise
            print(f"Warning: skipping language statistics for {repo['full_name']}: {error}")
            continue
        for language, amount in repo_languages.items():
            languages[language] = languages.get(language, 0) + amount
    top_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:5]
    language_total = sum(languages.values()) or 1

    write_asset(
        "hero.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-labelledby="title desc">
    <title id="title">{text(DISPLAY_NAME)} GitHub profile</title>
  <desc id="desc">C++ and Qt developer profile banner generated from GitHub data.</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#FDF8F4"/><stop offset="100%" stop-color="#F7F3EE"/></linearGradient><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="320" rx="38" fill="url(#bg)"/>
  <g transform="translate(80,94)">
    <text class="sans" font-size="22" font-weight="600" fill="#94AAB9">你好，我是</text>
    <text class="sans" y="72" font-size="64" font-weight="750" fill="#3C4F66">{text(DISPLAY_NAME)}</text>
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
    for label, value in (("Public Repos", len(repos)), ("Total Stars", total_stars), ("Followers", user.get("followers", 0)), ("Following", user.get("following", 0))):
        cards.append(f'<text class="sans" x="30" y="58" font-size="48" font-weight="700" fill="#3C4F66">{value}</text><text class="sans" x="30" y="92" font-size="16" fill="#8A9CAD">{label}</text>')
    card_groups = "".join(f'<g transform="translate({60 + index * 280},44)"><rect width="240" height="120" rx="20" fill="#FFFFFF" stroke="#E9EDF2" stroke-width="1.5"/>{card}</g>' for index, card in enumerate(cards))
    language_rows = []
    language_colors = ("#E0A07E", "#5668A3", "#347CC5", "#F0D84A", "#60438A")
    for index, (language, amount) in enumerate(top_languages):
        percent = round(amount * 100 / language_total)
        width = max(8, round(720 * percent / 100))
        color = language_colors[index % len(language_colors)]
        language_rows.append(f'<g transform="translate(0,{index * 44})"><text x="0" y="20" fill="#6F7F90">{text(language)}</text><rect x="150" y="0" width="720" height="28" rx="6" fill="#E9EDF2"/><rect x="150" y="0" width="{width}" height="28" rx="6" fill="{color}"/><text x="890" y="20" fill="#3C4F66" font-weight="600">{percent}%</text></g>')
    write_asset(
        "stats-overview.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500" role="img" aria-labelledby="title desc">
    <title id="title">{text(DISPLAY_NAME)} GitHub overview</title><desc id="desc">GitHub profile statistics generated from the GitHub API.</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs><rect width="1200" height="500" rx="28" fill="#FDF8F4"/>{card_groups}
  <text class="sans" x="60" y="220" font-size="24" font-weight="700" fill="#3C4F66">Top Languages</text><g transform="translate(60,270)" class="sans" font-size="18">{"".join(language_rows)}</g>
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
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="160" viewBox="0 0 1200 160" role="img" aria-labelledby="title desc"><title id="title">{text(DISPLAY_NAME)} profile highlights</title><desc id="desc">Profile highlights generated from the user's current projects and technologies.</desc><defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs><rect width="1200" height="160" rx="28" fill="#FDF8F4"/><g transform="translate(26,48)" class="sans" font-size="18" font-weight="600"><g><rect width="188" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">C++ / Qt</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">主要方向</text></g><g transform="translate(204,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">Python</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">脚本与自动化</text></g><g transform="translate(400,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">{text(project["name"])}</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">精选项目</text></g><g transform="translate(596,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">{text(project.get("language") or "项目")}</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">项目语言</text></g><g transform="translate(792,0)"><rect width="180" height="64" rx="18" fill="#FFFFFF" stroke="#E9EDF2"/><text x="40" y="29" fill="#3C4F66">GitHub</text><text x="40" y="51" font-size="14" font-weight="500" fill="#8A9CAD">持续维护</text></g></g></svg>
    ''',
    )

    language_names = " · ".join(text(language) for language, _ in top_languages) or "暂无语言数据"

    def section_asset(filename, title, subtitle):
        write_asset(
            filename,
            f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="150" viewBox="0 0 1200 150" role="img" aria-labelledby="title desc">
  <title id="title">{text(title)}</title>
  <desc id="desc">{text(subtitle)}</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="150" rx="28" fill="#FDF8F4"/>
  <text class="sans" x="60" y="62" font-size="32" font-weight="700" fill="#3C4F66">{text(title)}</text>
  <text class="sans" x="60" y="102" font-size="18" fill="#6F7F90">{text(subtitle)}</text>
  <rect x="950" y="66" width="150" height="8" rx="4" fill="#AFDADA"/>
</svg>
''',
        )

    tech_badges = (
        ("C++", "#9AAFC0"),
        ("Qt", "#8FB3C2"),
        ("Python", "#E8B98F"),
        ("CMake", "#A4B8A6"),
        ("Linux", "#C9C4B8"),
        ("VS Code", "#9EB8D6"),
        ("Git", "#E7B989"),
    )
    badge_groups = []
    badge_x = 60
    for label, color in tech_badges:
        badge_width = max(72, len(label) * 13 + 28)
        badge_groups.append(
            f'<g transform="translate({badge_x},178)"><rect width="{badge_width}" height="34" rx="3" fill="{color}"/><text class="sans" x="{badge_width / 2:.0f}" y="22" text-anchor="middle" font-size="16" font-weight="600" fill="#FFFFFF">{text(label)}</text></g>'
        )
        badge_x += badge_width + 12
    write_asset(
        "section-tech-stack.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="230" viewBox="0 0 1200 230" role="img" aria-labelledby="title desc">
  <title id="title">技术栈</title>
  <desc id="desc">GitHub 语言数据与主要开发技术。</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="150" rx="28" fill="#FDF8F4"/>
  <text class="sans" x="60" y="62" font-size="32" font-weight="700" fill="#3C4F66">技术栈</text>
  <text class="sans" x="60" y="102" font-size="18" fill="#6F7F90">GitHub 语言数据：{language_names}</text>
  <rect x="950" y="66" width="150" height="8" rx="4" fill="#AFDADA"/>
  {"".join(badge_groups)}
</svg>
''',
    )
    section_asset("section-activity.svg", "贡献活动", f"{USERNAME} 的 GitHub 贡献记录")
    section_asset("section-live-widgets.svg", "实时数据", "个人主页数据由 GitHub Actions 自动生成")


if __name__ == "__main__":
    main()
