# 主页配置说明

这个项目是一个由配置驱动的 GitHub 个人主页生成器。其他人只需要修改 `profile.config.json`，就可以复用同一套主页结构、SVG 资源和 GitHub Actions 工作流。

## 使用条件

1. 创建一个公开的 GitHub 同名主页仓库，例如用户 `alice` 需要创建 `alice/alice`。
2. 将本项目文件放入该仓库，并修改 `profile.config.json`。
3. 在仓库的 `Settings -> Actions -> General -> Workflow permissions` 中允许工作流写入仓库内容。
4. 推送到默认分支。三个工作流会根据账号自动生成统计图、贡献图和 Snake 动画。

不需要提供或提交个人访问令牌。工作流使用 GitHub 内置的 `GITHUB_TOKEN`；本地运行时也可以通过环境变量提供 Token，以提高 API 访问额度。

## 配置文件

### `README.template.md` 的作用

`README.template.md` 是个人主页的“版式模板”，不是 GitHub 最终展示的主页文件。它保存主页的固定结构和占位符，例如：

- `{{USERNAME}}`：替换为 GitHub 用户名
- `{{DISPLAY_NAME}}`：替换为显示名称
- `{{PROJECT_SECTIONS}}`：替换为配置中的精选项目卡片
- `{{GITEE_BLOCK}}`：根据 Gitee 配置生成链接或普通 Hero 图片
- `{{TELEGRAM_BLOCK}}`：根据 Telegram 配置生成联系项

脚本会把 `README.template.md`、`profile.config.json` 和 GitHub API 数据合并，生成最终的 `README.md`。GitHub 个人主页实际读取的是生成后的 `README.md`。

因此，修改主页结构时应该修改 `README.template.md`；修改账号、项目和个人信息时应该修改 `profile.config.json`。不要直接修改生成后的 `README.md`，因为下一次运行脚本或 GitHub Actions 时会被重新生成并覆盖。

### 必填配置

- `username`：GitHub 用户名，同时也是主页仓库名。
- `display_name`：Hero 横幅中的显示名称。
- `featured_projects`：精选项目数组，按数组顺序显示。每项包含：
  - `repo`：仓库全名，格式为 `owner/repository`。
  - `asset`：卡片 SVG 文件名，必须是当前目录下的 `.svg` 文件名，不能包含路径。

示例：

```json
"featured_projects": [
  {"repo": "alice/project-a", "asset": "pinned-project-a.svg"},
  {"repo": "alice/project-b", "asset": "pinned-project-b.svg"}
]
```

项目卡片会自动读取 GitHub API 返回的 Description、语言占比、Stars 和 Forks。

精选项目必须是公开仓库。生成器会拒绝读取私有仓库，避免在有权限的本地 Token 环境下把私有项目信息写入公开主页。

### 可选配置

- `bio`：README 中“关于我”的简介。
- `gitee_url`：Hero 横幅外层的跳转地址。不使用时填空字符串 `""`，Hero 将不带链接。
- `telegram.label`、`telegram.url`：联系信息。不使用时可以删除 `telegram`，README 不会生成空链接。
- `typing_lines`：动态打字签名的文字数组。
- `about.headline`：About 卡片标题。
- `about.motto`：About 卡片底部座右铭。
- `about.cards`：About 卡片内容，每项包含 `icon`、`title`、`subtitle`、`color`。
- `tech_stack`：技术栈标签数组，每项包含 `label` 和可选的 `color`。
- `theme`：主题颜色，包括 `background`、`panel`、`border`、`text`、`muted`、`subtle`、`accent` 和 `chart`。

颜色必须使用六位十六进制格式，例如 `#22D3EE`。不要把 Token、密码、私钥或其他敏感信息写入配置文件；这个文件会提交到公开仓库。

## 生成方式

### 推荐方式：推送后自动生成

修改 `profile.config.json` 后，直接提交并推送到 `main` 分支：

```powershell
git add profile.config.json README.template.md
git commit -m "configure profile"
git push origin main
```

`profile-assets.yml` 会在推送后自动运行，读取配置和 GitHub API 数据，生成并提交：

- `README.md`
- `assets/readme/*.svg`

因此，正常使用时不需要手动运行 Python 脚本。

### 可选方式：本地预览或排错

本地命令只用于在推送前检查生成结果，或者排查 GitHub Actions 问题：

```powershell
python scripts/update_profile_assets.py
```

本地运行需要网络访问 GitHub API；如果未设置 `GITHUB_TOKEN`，可能受到 API 匿名访问额度限制。

`README.md` 和 SVG 是生成文件，应该修改配置或 `README.template.md`，不要直接修改生成结果。

