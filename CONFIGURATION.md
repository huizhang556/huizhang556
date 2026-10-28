# 主页配置说明

这个项目是一个由配置驱动的 GitHub 个人主页生成器。其他人只需要修改 `profile.config.json`，就可以复用同一套主页结构、SVG 资源和 GitHub Actions 工作流。

## 使用条件

1. 创建一个公开的 GitHub 同名主页仓库，例如用户 `alice` 需要创建 `alice/alice`。
2. 将本项目文件放入该仓库，并修改 `profile.config.json`。
3. 在仓库的 `Settings -> Actions -> General -> Workflow permissions` 中允许工作流写入仓库内容。
4. 推送到默认分支。三个工作流会根据账号自动生成统计图、贡献图和 Snake 动画。

不需要提供或提交个人访问令牌。工作流使用 GitHub 内置的 `GITHUB_TOKEN`；本地运行时也可以通过环境变量提供 Token，以提高 API 访问额度。

## 配置文件

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

本地生成：

```powershell
python scripts/update_profile_assets.py
```

生成器会更新：

- `README.md`
- `assets/readme/*.svg`

`README.md` 和 SVG 是生成文件，应该修改配置或 `README.template.md`，不要直接修改生成结果。

## 两个 GitHub 账号

同一份代码可以服务多个账号，但每个账号必须使用独立的仓库和独立的配置：

```text
账号 A -> alice/alice -> profile.config.json 中 username=alice
账号 B -> bob/bob     -> profile.config.json 中 username=bob
```

不要让两个账号共用同一个远程仓库，否则工作流会把账号 A 和账号 B 的数据互相覆盖。推荐为每个账号复制一份仓库，分别修改配置并分别推送。
