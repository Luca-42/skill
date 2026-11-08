---
name: dsh-plugin-market
description: "为 DSH 插件编写市场索引（index.json）、托管到 GitHub Pages、把仓库转为公开，并在 DSH「发现」页添加索引源。当插件已发布到 npm、需要上架 DSH 插件市场，或市场索引不生效/图标 404/版本不更新时使用。"
license: MIT
metadata:
  version: "1.0"
  author: Luca-42
---

# DSH 插件市场索引

DSH 插件市场是一个静态 JSON 索引，列出可安装的插件版本。索引里每个版本指向
npm 包或 Git 仓库的某个 commit。

## 索引文件

放在仓库里、由 GitHub Pages 托管，例如 `docs/index.json`（Pages 选 `/docs` 目录）。

```json
{
  "format": 1,
  "title": { "en": "My plugins", "zh": "我的插件" },
  "metadata": {
    "categories": { "translation": { "title": { "en": "Translation", "zh": "翻译" } } }
  },
  "plugins": [
    {
      "name": "dsh-plugin-example",
      "title": { "en": "Example", "zh": "示例" },
      "description": { "en": "...", "zh": "..." },
      "icon": "icon.svg",
      "author": "your-name",
      "homepage": "https://github.com/<owner>/<repo>#readme",
      "repository": { "url": "https://github.com/<owner>/<repo>" },
      "metadata": { "category": "translation" },
      "versions": [
        {
          "version": "0.2.0",
          "publishTimestamp": 1794129939,
          "source": { "type": "npm" }
        }
      ]
    }
  ]
}
```

要点：

- `format` 必须是 `1`；`plugins` 必填。
- `name` 必须与 npm 包名一致（或与 Git 仓库版本对应）。
- `versions[].source`：`{ "type": "npm" }` 或
  `{ "type": "git", "url": "https://...", "commit": "<40 位 sha>", "path": "<子目录>" }`。
- `publishTimestamp` 用 npm registry 里该版本的发布时间（秒级 epoch）：
  `https://registry.npmjs.org/<pkg>` 的 `time[version]` 换算。
- `icon`：内联 `data:` URL，或**相对索引 URL 解析**的路径（不要写 `/icon.svg`，会从站点根解析）。
  图标 ≤32 KiB。
- `engines.dsh` 可选；写了就要与包自身声明一致，否则安装器会拒。包内没有该字段就省略。
- 约束：索引 ≤128 MiB、返回 2xx、不经重定向。

## 宿主与公开

1. **仓库转公开**：私有仓库无法用免费 GitHub Pages，npm 源码链接与索引地址也都要求公开可读。
   GitHub → 仓库 → Settings → General → Danger Zone → Change visibility → Make public。
2. **启用 Pages**：Settings → Pages → Source: Deploy from a branch →
   Branch `main`、Folder `/docs` → Save。
3. 1~2 分钟后索引地址：`https://<owner>.github.io/<repo>/index.json`。

验证：

```bash
curl -s https://<owner>.github.io/<repo>/index.json | head -3
# 期望：{ "format": 1, ...
curl -s https://api.github.com/repos/<owner>/<repo> | grep -E '"(visibility|private)"'
```

## 在 DSH 里添加

插件页 → **发现** → **添加索引源** → 粘贴索引 URL → 浏览并安装。

## 常见问题

- **索引能打开但市场不显示插件**：检查 `format`、`name`、`versions[].source`；DSH 只校验格式，不校验内容真伪。
- **图标 404**：`icon` 用相对路径，且图标文件与索引同目录（或相对其解析）。
- **版本不更新**：Pages 有 CDN 缓存，push 后等 1~2 分钟；DSH 端也缓存索引，重新添加索引源或重启 dsh。
- **发布新版本后**：同时更新 `versions` 里的条目和 `publishTimestamp`，否则市场仍显示旧版本。
- **私有仓库**：Pages 需要付费计划；先转公开。
