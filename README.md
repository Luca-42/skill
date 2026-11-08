# dsh-skills

仓库：<https://github.com/Luca-42/skill>

Luca-42 的 DSH（DeepSeek Harness）技能集合。每个技能是一个目录，内含 `SKILL.md`
（YAML frontmatter + 操作说明），按需加载。

## 技能列表

| 技能 | 用途 | 典型触发 |
|---|---|---|
| [`github-push-ssh443`](skills/github-push-ssh443/SKILL.md) | 在 22 端口被封的网络里可靠推送 GitHub（走 `ssh.github.com:443`） | `git push` 报 Repository not found / Permission denied / 空仓库推不上去 |
| [`npm-publish-2fa`](skills/npm-publish-2fa/SKILL.md) | 在开启 2FA 的 npm 账号上发布包（bypass token、临时 userconfig、staged 占位） | `npm publish` 报 403 two-factor / need auth / 只看到 `0.0.0-stage` |
| [`dsh-plugin-market`](skills/dsh-plugin-market/SKILL.md) | 写 DSH 插件市场索引、托管 GitHub Pages、转公开仓库 | 插件要上架「发现」市场、索引不生效、图标 404 |

## 使用方式

**方式一：放进工作区**
把某个技能目录复制到你的 DSH 工作区下的 `skills/` 目录，会话即可按需加载：

```bash
mkdir -p <workspace>/skills
cp -r skills/github-push-ssh443 <workspace>/skills/
```

**方式二：随插件包分发**
如果技能服务于某个 DSH 插件，把 `skills/` 放进插件包并在 `package.json` 的 `files` 里声明，
DSH 安装插件后会随包提供。

## 约定

- 每个 `SKILL.md` 的 frontmatter 至少包含 `name` 与 `description`；
  `description` 写清楚「做什么 + 什么时候用」，便于自动匹配。
- 内容以可执行的步骤、命令、报错对照为主，避免大段背景叙述。
- 不在技能里写 token、私钥、内网地址等敏感信息。

## 许可证

MIT
