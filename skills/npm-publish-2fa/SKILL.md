---
name: npm-publish-2fa
description: "在开启 2FA 的 npm 账号上发布包（尤其是首次发布新包）：bypass-2FA token、临时 userconfig、官方 registry、dry-run 检查、staged 0.0.0-stage 占位的识别与处理、发布后验证。当 npm publish 报 403 two-factor、need auth、或新包首次发布时 registry 只显示 0.0.0-stage 时使用。"
license: MIT
metadata:
  version: "1.0"
  author: Luca-42
---

# npm 发布（2FA 账号）

适用于账号启用 2FA、用 token 从命令行/agent 发布 npm 包的场景。

## 前置条件

- 账号开启 2FA 时，普通 granular token 发布会报：

  ```
  403 ... Two-factor authentication or granular access token with bypass 2fa enabled is required
  ```

  解决方式（二选一）：
  - 给 granular token 勾上 **Bypass 2FA**；
  - 使用 classic **Automation** token（天生免 2FA，适合 CI/脚本）。
- 确认 registry：`npm config get registry`。国内机器常被设为 npmmirror，
  **发布必须显式指定官方源**，或在包内加 `publishConfig.registry`。

## 认证：临时 userconfig（用完即删）

把 token 写进临时 userconfig，而不是 `~/.npmrc` 或命令行明文。

- `--userconfig` 必须用 **Windows 路径**：Git Bash 的 `/tmp`、MSYS 风格路径 npm 可能不认，
  表现为 `need auth`。
- 文件权限 0600，用完删除，绝不进仓库/文档/日志。

```bash
RC="C:/Users/<user>/AppData/Local/Temp/dsh-npmrc"
umask 077
printf 'registry=https://registry.npmjs.org/\n//registry.npmjs.org/:_authToken=%s\n' "$NPM_TOKEN" > "$RC"

npm --userconfig "$RC" --registry=https://registry.npmjs.org/ whoami
npm --userconfig "$RC" --registry=https://registry.npmjs.org/ publish --dry-run
npm --userconfig "$RC" --registry=https://registry.npmjs.org/ publish
rm -f "$RC"
```

## 发布前检查

- `package.json` 去掉 `private: true`（npm 直接拒绝 private 包）；
- `repository.url` 写成 `git+https://...`，避免 npm 自动纠正的 warning；
- `npm publish --dry-run` 核对 tarball 清单与体积；
- 新包先确认包名可用：`curl -s -o /dev/null -w '%{http_code}' https://registry.npmjs.org/<pkg>`（404 = 可用）。

## 首次发布的两个坑

1. **staged 占位版本**：npm 首次发布新包会先创建 `0.0.0-stage`
   （描述 “Temporary package placeholder for staged publishing”），
   真正的版本稍后才出现。**registry 暂时只显示 `0.0.0-stage` 不代表失败**——
   等几分钟再查，不要立刻重发（重发会报 `You cannot publish over the previously published versions`）。
2. **占位版本删不掉**：用 bypass-2FA 的 granular token 执行
   `npm unpublish <pkg>@0.0.0-stage` 会报
   `Granular access tokens that bypass two-factor authentication may not perform this action`。
   只能去 npm 网站手动删（72 小时内），或留着不管（不影响 `latest`）。

## staged 相关工具

npm 10.x 没有 `npm stage` 子命令。需要查看/批准 staged 版本（npm 11+）时：

```bash
npx -y npm@11 stage list [<pkg>]
npx -y npm@11 stage approve <stage-id>
```

## 发布后验证

```bash
curl -s https://registry.npmjs.org/<pkg>/<version> \
  | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{const j=JSON.parse(s);console.log(j.name,j.version,j.dist.tarball,j.dist.shasum)})"
```

- 打 tag 并推送：`git tag -a v<version> -m "..." && git push origin v<version>`；
- README 补安装方式；
- **token 一旦出现在聊天、日志或临时文件里就视为已泄露，立即轮换**。
