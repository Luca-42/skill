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
| [`pixel-art-restore`](skills/pixel-art-restore/SKILL.md) | 把 AI 生成/网传的「伪像素画」还原成真像素资产：网格体检、proper-pixel-art(ppa) 还原、干净去背、散点清理、验收与整数倍缩放 | 图看着像素但格子不齐/边缘发虚、要还原 sprite 真实分辨率、要批量处理像素图、纠结「还原原网格」还是「降采样转像素」 |
| [`rembg-cutout`](skills/rembg-cutout/SKILL.md) | 用 rembg（ONNX 深度学习分割）在高清图上 AI 抠图去背，输出透明底 PNG；含环境部署、模型选型、下载排障、参数与验收 | 要抠图/去背/去背景、抠发丝与褶边、为像素画或立绘准备透明底、模型下载报 10054/SSL 错误 |
| [`zhaopin-collect`](skills/zhaopin-collect/SKILL.md) | 采集考公 / 考编 / 央国企在招信息：4 路分片并发、省考雷达、岗位表下载与 10KB 校验 | `跑今天的招聘采集`、更新在招清单、看看这几天有什么新公告 |
| [`zhaopin-list-build`](skills/zhaopin-list-build/SKILL.md) | 把采集分片合并成清单：按日期/时刻判状态、校验岗位表、生成今日变化与截止提醒 | `生成清单`、重建台账、自检一下、今天有什么变化、这周什么时候截止 |

配套使用：杂乱背景的图先 `rembg-cutout` 在高清原图上抠图，再 `pixel-art-restore` 像素化；不要先像素化再手工抠。


> 注：`zhaopin-collect` / `zhaopin-list-build` 依赖一套工作区脚本（`脚本/dl.py`、`build_list.py`、`verify.py`、`sync_raw.py`、`diff_report.py`、`day_alert.py`）与固定的目录约定（`数据/raw_*.json`、`数据/units.json`、`岗位列表/{考公,考编,央国企}/`）。换机器时需一并带上 `脚本/`，或按 SKILL.md 里的命令替换成等价实现。

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
