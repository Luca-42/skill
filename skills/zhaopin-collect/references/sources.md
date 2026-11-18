# 数据源实测清单（2026-10 ~ 2026-11）

> 站点行为会变。这里记的是"当时实测 + 可行的绕法"，不是永久结论。
> 遇到与本文不符，以实测为准，并顺手更新本文。

## 稳定可取

| 站点 | 用途 | 备注 |
| --- | --- | --- |
| `dl.scs.gov.cn/api/gkhome/*` | 国考专题站文章/资源列表 | JSON 接口，偶尔返回 `{"exam":"error"}`，重试即可 |
| `dl.scs.gov.cn/download/{id}` | 国考招考简章 zip | 绕过页面图形验证码的官方资源接口 |
| `scpta.com.cn` | 四川人事考试网 | 省考公告 + 职位表 xlsx，服务端渲染 |
| `jshrss.jiangsu.gov.cn` / 江苏报名系统 | 江苏省考 | 附件直链需从页面 `data-link` 取 |
| `gwy.sdrsks.org.cn` | 山东人事考试 | 有"报名情况公示"可佐证报名已开 |
| `gwy.zjks.gov.cn`（http） | 浙江公务员录用网 | https 常超时，用 http；首页有"今天是…"可判活 |
| `www.bjdj.gov.cn` / `rsj.beijing.gov.cn/bm/ztzl/gwy/` | 北京组工 / 北京人事考试 | 报名入口落地 `fuwu.rsj.beijing.gov.cn/gwy/main` |
| `www.xiongan.gov.cn/tzgg.html` | 雄安新区通知公告 | 招聘类公告混在采购/公示里，需要筛 |
| `chinaxiongan.cn/zhaopingonggao.html` | 雄安集团招聘 | 更新慢，社招为主 |
| `sasac.gov.cn`（人事招聘栏目） | 国资委转载央企校招 | 正文常是图片海报 |
| `job.mohrss.gov.cn/qyzp/` | 中国公共招聘网央企专栏 | **https 不通，必须 http** |
| `ncss.cn` | 国家大学生就业服务平台 | 教育部，公告全文可读 |
| `offcn.com` 各国企/银行/教师频道 | 中公转载 | 正文最全，但附件常缺失；标题带"岗位表下载"的多是 SEO 引流稿 |
| `huatu.com` 各省站 | 华图转载 | 有"有附件"标签，实际多为空 |
| `qgsydw.com` | 全国事业单位招聘网 | 可作国网等大公告的镜像源 |

## 反爬 / 不可达（别死磕）

| 站点 | 现象 | 绕法 |
| --- | --- | --- |
| `zhaopin.sgcc.com.cn`（国网） | 全线 412（瑞数 WAF），含省公司站 | 中公 tag 页 / 国资委 / 镜像站；**注意 SEO 稿不算发布** |
| `zhaopin.cnpc.com.cn`（中石油） | 412 | 中公转载 |
| `zhaopin.chng.com.cn`（华能） | 403 / 448B 外壳 | 高校就业网同源页 |
| `zhaopin.chinacoal.com`（中煤） | 405 | 中南大学等高校页（服务端渲染职位列表） |
| `job.sinochem.com`（中化） | 403；北森 `*.hotjob.cn` 843B 外壳；国聘 604B 外壳 | **多轮均失败**，中化从不发可下载岗位表 |
| `www.cnnc.com.cn`（中核） | 412；`job.cnnc.com.cn` DNS 解析失败 | 高校就业网 + 学院转载 |
| `spacechina.com`（航天科技） | 403 / 超时 | 高校就业网 |
| `cdb.com.cn`（国开行） | 412 | 国家大学生就业服务平台 |
| `ccb.com` / `job2.ccb.com` / `bankcomm.com` / `job.icbc.com.cn` / `10086.cn` | legacy TLS renegotiation 被禁 | `ssl.OP_LEGACY_SERVER_CONNECT`，或改用转载页 |
| `rczp.china-railway.com.cn`（国铁） | 列表接口要 AES 加密，明文 POST 一律 500；需登录 | 走子企业/铁科院公告转载 |
| `tobacco.gov.cn` | 连接超时 | 用 `cpta.com.cn`（中国人事考试网）官方公告 |
| `mohrss.gov.cn` 部分页 | 986 字节 JS 反爬跳转（EO_Bot） | 用子站或 `job.mohrss.gov.cn` |
| `www.scs.gov.cn` | 987 字节 JS 反爬壳 | 走 `dl.scs.gov.cn` 接口 |
| `gwy.zjks.gov.cn/zjgwy/...` | 45s 超时 | 用根域或中公雷达页交叉核对 |

## 前端渲染（只能存 HTML 外壳，无附件）

国聘微站 `*.iguopin.com`、北森 `*.hotjob.cn` / `wecruit` / `*.zhiye.com`、智联 `zhipin.com`、`zhaopin.csg.cn`（南网）、`job.10086.cn`、`zhaopin.ccccltd.cn`（中交建）、`zhaopin.powerchina.cn`（电建）。

判定方法：抓下来只有 600B ~ 4KB，内容是一个 `<div id="root">` 或 `<script src="/static/js/main.*.js">`。
存档方式：`dl.py get --name "<单位>_岗位查询页.html"`，`下载状态` 记 `未找到附件`，备注写"在线岗位库"。

## 才立方（高校就业网）站群

`*.jysd.com` / `*.91wllm.cn` / `*.nmbys.cn` / `*.cqbys.com` 等。

- **详情页**：状态反复。2026-11-09 前后 5 站（cqu / xmu / nxujob / hebust / ccnu）恢复静态可取；其余仍跳统一身份认证。
- **列表页**：一直是 JS 混淆壳，**不能用来发现公告**，只能直接访问已知详情 URL。
- 详情页正文有时是 zlib + base64（含二次 base64）内嵌，需要解码才能拿到正文。
- "过期时间"字段是**页面展示期**，不等于报名截止日。当截止日用时必须在备注注明口径。

## 聚合站的使用纪律

- 中公/华图的**省份汇总表**是省考雷达的主要来源，但要交叉两三个页面——单页表格会滞后（曾出现总站北京行仍灰色、分站已更新）。
- 中公的 `tag/` 页会批量生成 SEO 引流稿，标题像"XX 岗位表下载""XX 报名入口"，正文只有模板。**判定发布的标准是看到正式公告或岗位计划，不是看到标题。**
