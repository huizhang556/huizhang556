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


def truncate_lines(value, line_limit, max_lines):
    value = str(value or "").strip()
    lines = []
    start = 0
    while start < len(value):
        end = min(start + line_limit, len(value))
        word_end = end
        while (
            start < word_end < len(value)
            and value[word_end - 1].isascii()
            and value[word_end].isascii()
            and (value[word_end - 1].isalnum() or value[word_end - 1] in "-_/.+")
            and (value[word_end].isalnum() or value[word_end] in "-_/.+")
        ):
            word_end -= 1
        lines.append(value[start : word_end if word_end > start else end])
        start = word_end if word_end > start else end
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: line_limit - 3].rstrip() + "..."
    return lines or [""]


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


def write_project_card(project, filename):
    project_languages = get_json(project["languages_url"])
    project_description_lines = truncate_lines(
        project.get("description") or "暂无项目描述", line_limit=22, max_lines=2
    )
    project_language_rows = sorted(
        project_languages.items(), key=lambda item: item[1], reverse=True
    )
    project_language_total = sum(project_languages.values())
    project_language_colors = (
        "#A78BFA",
        "#60A5FA",
        "#F59E0B",
        "#34D399",
        "#22D3EE",
        "#64748B",
    )
    if project_language_total:
        visible_languages = project_language_rows[:5]
        other_amount = sum(amount for _, amount in project_language_rows[5:])
        if other_amount:
            visible_languages.append(("Other", other_amount))
    else:
        visible_languages = []

    pie_center_x = 560
    pie_center_y = 110
    pie_radius = 44
    pie_circumference = 2 * 3.141592653589793 * pie_radius
    pie_segments = []
    pie_legend = []
    pie_offset = 0
    for index, (language, amount) in enumerate(visible_languages):
        segment_length = pie_circumference * amount / project_language_total
        color = project_language_colors[index % len(project_language_colors)]
        pie_segments.append(
            f'<circle cx="{pie_center_x}" cy="{pie_center_y}" r="{pie_radius}" fill="none" stroke="{color}" stroke-width="22" stroke-dasharray="{segment_length:.2f} {pie_circumference - segment_length:.2f}" stroke-dashoffset="{-pie_offset:.2f}"/>'
        )
        percent = amount * 100 / project_language_total
        pie_legend.append(
            f'<g transform="translate(650,{58 + index * 25})"><circle cx="5" cy="-5" r="5" fill="{color}"/><text class="sans" x="18" y="0" font-size="14" fill="#C4B5FD">{text(language)}</text><text class="sans" x="130" y="0" font-size="14" text-anchor="end" fill="#94A3B8">{percent:.1f}%</text></g>'
        )
        pie_offset += segment_length
    if not visible_languages:
        pie_segments.append(
            f'<circle cx="{pie_center_x}" cy="{pie_center_y}" r="{pie_radius}" fill="none" stroke="#334155" stroke-width="22"/>'
        )
        pie_legend.append(
            '<text class="sans" x="650" y="110" font-size="14" fill="#94A3B8">No language data</text>'
        )
    project_language_chart = f'''<g transform="rotate(-90 {pie_center_x} {pie_center_y})">{"".join(pie_segments)}</g>
  <circle cx="{pie_center_x}" cy="{pie_center_y}" r="30" fill="#111827"/>
  <text class="sans" x="{pie_center_x}" y="{pie_center_y + 5}" text-anchor="middle" font-size="12" font-weight="600" fill="#C4B5FD">Tech</text>
  {"".join(pie_legend)}'''
    write_asset(
        filename,
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="220" viewBox="0 0 1200 220" role="img" aria-labelledby="title desc">
  <title id="title">{text(project["name"])} project card</title>
  <desc id="desc">Generated project card for the user's featured GitHub repository.</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="220" rx="30" fill="#111827" stroke="#334155" stroke-width="1.5"/>
  <text class="sans" x="48" y="78" font-size="44" font-weight="700" fill="#F8FAFC">{text(project["name"])}</text>
  <text class="sans" x="48" y="119" font-size="18" fill="#CBD5E1">{text(project_description_lines[0])}</text>
  <text class="sans" x="48" y="148" font-size="18" fill="#CBD5E1">{text(project_description_lines[1] if len(project_description_lines) > 1 else "")}</text>
  {project_language_chart}
  <g transform="translate(940,64)">
    <text class="sans" font-size="26" font-weight="700" fill="#F8FAFC">{project.get("stargazers_count", 0)}</text>
    <text class="sans" y="26" font-size="14" fill="#94A3B8">Stars</text>
    <g transform="translate(90,0)">
      <text class="sans" font-size="26" font-weight="700" fill="#F8FAFC">{project.get("forks_count", 0)}</text>
      <text class="sans" y="26" font-size="14" fill="#94A3B8">Forks</text>
    </g>
  </g>
</svg>
''',
    )


def main():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    repos = get_public_repos()
    original_repos = [repo for repo in repos if not repo.get("fork", False)]
    projects = [
        get_json(f"https://api.github.com/repos/{USERNAME}/pc-video-player"),
        get_json(f"https://api.github.com/repos/{USERNAME}/{PROJECT}"),
    ]
    project = projects[-1]

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    languages = {}
    for repo in original_repos:
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
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#111827"/><stop offset="100%" stop-color="#1E293B"/></linearGradient><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="320" rx="38" fill="url(#bg)"/>
  <g transform="translate(80,94)">
    <text class="sans" font-size="22" font-weight="600" fill="#7DD3FC">你好，我是</text>
    <text class="sans" y="72" font-size="64" font-weight="750" fill="#F8FAFC">{text(DISPLAY_NAME)}</text>
    <text class="sans" y="126" font-size="28" fill="#CBD5E1">C++ / Qt 开发者</text>
    <text class="sans" y="174" font-size="22" font-weight="650" fill="#22D3EE" text-decoration="underline">同步Gitee主页 : https://gitee.com/huizhang556</text>
  </g>
  <g transform="translate(810,64)">
    <rect width="340" height="180" rx="26" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
    <text class="sans" x="30" y="42" font-size="15" font-weight="700" fill="#94A3B8">GitHub 概览</text>
    <g transform="translate(30,80)"><text class="sans" font-size="38" font-weight="700" fill="#F8FAFC">{len(repos)}</text><text class="sans" y="26" font-size="16" fill="#94A3B8">仓库</text></g>
    <g transform="translate(145,80)"><text class="sans" font-size="38" font-weight="700" fill="#F8FAFC">{total_stars}</text><text class="sans" y="26" font-size="16" fill="#94A3B8">Stars</text></g>
    <g transform="translate(248,80)"><text class="sans" font-size="38" font-weight="700" fill="#F8FAFC">{user.get("followers", 0)}</text><text class="sans" y="26" font-size="16" fill="#94A3B8">关注者</text></g>
  </g>
</svg>
''',
    )

    write_asset(
        "about-me.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="260" viewBox="0 0 1200 260" role="img" aria-labelledby="title desc">
  <title id="title">{text(DISPLAY_NAME)} about</title>
  <desc id="desc">C++ and Qt developer focused on desktop applications, automation, multi-platform development, and AI tools.</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="260" rx="28" fill="#111827"/>
  <text class="sans" x="50" y="48" font-size="22" font-weight="600" fill="#F8FAFC">C++ / Qt 开发者，专注桌面应用与自动化工具</text>
  <g transform="translate(40,78)">
    <rect width="260" height="82" rx="16" fill="#1E293B" stroke="#334155"/>
    <circle cx="34" cy="41" r="20" fill="#60A5FA"/><text class="sans" x="34" y="46" text-anchor="middle" font-size="11" font-weight="700" fill="#111827">C++</text>
    <text class="sans" x="70" y="36" font-size="18" font-weight="700" fill="#F8FAFC">C++ / Qt</text><text class="sans" x="70" y="59" font-size="14" fill="#CBD5E1">桌面应用开发</text>
  </g>
  <g transform="translate(330,78)">
    <rect width="260" height="82" rx="16" fill="#1E293B" stroke="#334155"/>
    <circle cx="34" cy="41" r="20" fill="#F59E0B"/><text class="sans" x="34" y="46" text-anchor="middle" font-size="12" font-weight="700" fill="#111827">PY</text>
    <text class="sans" x="70" y="36" font-size="18" font-weight="700" fill="#F8FAFC">Python</text><text class="sans" x="70" y="59" font-size="14" fill="#CBD5E1">脚本与自动化</text>
  </g>
  <g transform="translate(620,78)">
    <rect width="260" height="82" rx="16" fill="#1E293B" stroke="#334155"/>
    <circle cx="34" cy="41" r="20" fill="#A78BFA"/><text class="sans" x="34" y="46" text-anchor="middle" font-size="10" font-weight="700" fill="#111827">WEB</text>
    <text class="sans" x="70" y="36" font-size="18" font-weight="700" fill="#F8FAFC">多端开发</text><text class="sans" x="70" y="59" font-size="14" fill="#CBD5E1">Web / Android / 微信</text>
  </g>
  <g transform="translate(910,78)">
    <rect width="250" height="82" rx="16" fill="#1E293B" stroke="#334155"/>
    <circle cx="34" cy="41" r="20" fill="#34D399"/><text class="sans" x="34" y="46" text-anchor="middle" font-size="12" font-weight="700" fill="#111827">AI</text>
    <text class="sans" x="70" y="36" font-size="18" font-weight="700" fill="#F8FAFC">AI 工具</text><text class="sans" x="70" y="59" font-size="14" fill="#CBD5E1">效率与开发辅助</text>
  </g>
  <text class="sans" x="50" y="215" font-size="22" font-weight="600" fill="#CBD5E1">“世上无难事，只怕有心人。”</text>
</svg>
''',
    )

    cards = []
    for label, value in (("Public Repos", len(repos)), ("Total Stars", total_stars), ("Followers", user.get("followers", 0)), ("Following", user.get("following", 0))):
        cards.append(f'<text class="sans" x="30" y="58" font-size="48" font-weight="700" fill="#F8FAFC">{value}</text><text class="sans" x="30" y="92" font-size="16" fill="#94A3B8">{label}</text>')
    card_groups = "".join(f'<g transform="translate({60 + index * 280},44)"><rect width="240" height="120" rx="20" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>{card}</g>' for index, card in enumerate(cards))
    language_rows = []
    language_colors = ("#22D3EE", "#60A5FA", "#A78BFA", "#F59E0B", "#34D399")
    for index, (language, amount) in enumerate(top_languages):
        percent = round(amount * 100 / language_total)
        width = max(8, round(720 * percent / 100))
        color = language_colors[index % len(language_colors)]
        language_rows.append(f'<g transform="translate(0,{index * 44})"><text x="0" y="20" fill="#CBD5E1">{text(language)}</text><rect x="150" y="0" width="720" height="28" rx="6" fill="#334155"/><rect x="150" y="0" width="{width}" height="28" rx="6" fill="{color}"/><text x="890" y="20" fill="#F8FAFC" font-weight="600">{percent}%</text></g>')
    write_asset(
        "stats-overview.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500" role="img" aria-labelledby="title desc">
        <title id="title">{text(DISPLAY_NAME)} GitHub overview</title><desc id="desc">GitHub profile statistics generated from the GitHub API. Language statistics use original repositories only.</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs><rect width="1200" height="500" rx="28" fill="#111827"/>{card_groups}
  <text class="sans" x="60" y="220" font-size="24" font-weight="700" fill="#F8FAFC">Top Languages</text><text class="sans" x="270" y="220" font-size="14" fill="#94A3B8">Original repositories only</text><g transform="translate(60,270)" class="sans" font-size="18">{"".join(language_rows)}</g>
</svg>
''',
    )

    write_project_card(projects[0], "pinned-pc-video-player.svg")
    write_project_card(projects[1], "pinned-bbdown.svg")

    write_asset(
        "achievements.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="160" viewBox="0 0 1200 160" role="img" aria-labelledby="title desc"><title id="title">{text(DISPLAY_NAME)} profile highlights</title><desc id="desc">Profile highlights generated from the user's current projects and technologies.</desc><defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs><rect width="1200" height="160" rx="28" fill="#111827"/><g transform="translate(26,48)" class="sans" font-size="18" font-weight="600"><g><rect width="188" height="64" rx="18" fill="#1E293B" stroke="#334155"/><text x="40" y="29" fill="#F8FAFC">C++ / Qt</text><text x="40" y="51" font-size="14" font-weight="500" fill="#94A3B8">主要方向</text></g><g transform="translate(204,0)"><rect width="180" height="64" rx="18" fill="#1E293B" stroke="#334155"/><text x="40" y="29" fill="#F8FAFC">Python</text><text x="40" y="51" font-size="14" font-weight="500" fill="#94A3B8">脚本与自动化</text></g><g transform="translate(400,0)"><rect width="180" height="64" rx="18" fill="#1E293B" stroke="#334155"/><text x="40" y="29" fill="#F8FAFC">{text(project["name"])}</text><text x="40" y="51" font-size="14" font-weight="500" fill="#94A3B8">精选项目</text></g><g transform="translate(596,0)"><rect width="180" height="64" rx="18" fill="#1E293B" stroke="#334155"/><text x="40" y="29" fill="#F8FAFC">{text(project.get("language") or "项目")}</text><text x="40" y="51" font-size="14" font-weight="500" fill="#94A3B8">项目语言</text></g><g transform="translate(792,0)"><rect width="180" height="64" rx="18" fill="#1E293B" stroke="#334155"/><text x="40" y="29" fill="#F8FAFC">GitHub</text><text x="40" y="51" font-size="14" font-weight="500" fill="#94A3B8">持续维护</text></g></g></svg>
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
  <rect width="1200" height="150" rx="28" fill="#111827"/>
  <text class="sans" x="60" y="62" font-size="32" font-weight="700" fill="#F8FAFC">{text(title)}</text>
  <text class="sans" x="60" y="102" font-size="18" fill="#CBD5E1">{text(subtitle)}</text>
  <rect x="950" y="66" width="150" height="8" rx="4" fill="#22D3EE"/>
</svg>
''',
        )

    tech_badges = (
        ("C++", "#60A5FA"),
        ("Qt", "#38BDF8"),
        ("Python", "#F59E0B"),
        ("CMake", "#34D399"),
        ("Linux", "#64748B"),
        ("VS Code", "#A78BFA"),
        ("Git", "#22D3EE"),
    )
    badge_groups = []
    badge_x = 250
    for label, color in tech_badges:
        badge_width = max(72, len(label) * 13 + 28)
        badge_groups.append(
            f'<g transform="translate({badge_x},178)"><rect width="{badge_width}" height="34" rx="3" fill="{color}"/><text class="sans" x="{badge_width / 2:.0f}" y="22" text-anchor="middle" font-size="16" font-weight="600" fill="#111827">{text(label)}</text></g>'
        )
        badge_x += badge_width + 12
    write_asset(
        "section-tech-stack.svg",
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="230" viewBox="0 0 1200 230" role="img" aria-labelledby="title desc">
  <title id="title">技术栈</title>
  <desc id="desc">GitHub 原创仓库语言数据与主要开发技术。</desc>
  <defs><style>.sans{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}</style></defs>
  <rect width="1200" height="150" rx="28" fill="#111827"/>
  <text class="sans" x="60" y="62" font-size="32" font-weight="700" fill="#F8FAFC">技术栈</text>
  <text class="sans" x="60" y="102" font-size="18" fill="#CBD5E1">原创仓库语言数据：{language_names}</text>
  <rect x="950" y="66" width="150" height="8" rx="4" fill="#22D3EE"/>
  {"".join(badge_groups)}
</svg>
''',
    )
    section_asset("section-live-widgets.svg", "实时数据", "个人主页数据由 GitHub Actions 自动生成")


if __name__ == "__main__":
    main()
