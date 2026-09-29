# Profile Configuration

This repository is reusable for any public GitHub profile. Edit `profile.config.json`, then run the asset workflow or run the generator locally.

Required fields:

- `username`: GitHub username. The repository should be the user's same-name profile repository.
- `display_name`: Name shown in the hero banner.
- `featured_projects`: Ordered list of repositories. Each item uses `repo` in `owner/name` format and a unique SVG `asset` filename.

Optional fields configure the rest of the page:

- `bio`: Introductory sentence in the About section.
- `gitee_url`: Link used by the hero banner. Set it to an empty string if unused.
- `telegram.label` and `telegram.url`: Contact link. Replace or remove this line in `README.template.md` for another contact method.
- `typing_lines`: Lines shown by the animated typing banner.
- `about.headline`, `about.motto`, and `about.cards`: About section content.
- `tech_stack`: Labels shown in the technology stack section.
- `theme`: Background, panel, text, border, accent, and chart colors.

The generated `README.md` and `assets/readme/*.svg` files should not be edited directly. Change the configuration or `README.template.md`, then regenerate them.

The three workflows use the repository's `GITHUB_TOKEN`; no personal access token is required. Enable Actions and allow workflows to write repository contents under Settings > Actions > General > Workflow permissions.
