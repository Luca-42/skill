# pixel-art-restore 安装说明

本目录就是 skill 包 `pixel-art-restore`（也可打包成 `pixel-art-restore.zip` 分发），作用是**把 AI 生成的伪像素图还原成真像素资产**。请按下面四步装好。

---

## 1. 落位（不要改名、不要拆散文件）

目录 `pixel-art-restore/` 内含：

```
pixel-art-restore/
├── SKILL.md                    # 技能定义与完整工作流
├── INSTALL.md                  # 本文件
├── scripts/
│   ├── measure_grid.py         # 网格体检：判断该还原还是该转换
│   ├── key_bg.py               # 干净去背 + 残边清理 + 放大预览
│   └── batch_restore.py        # 批量还原整个文件夹
└── references/
    ├── ppa-cli.md              # ppa 全部参数与已知行为
    └── restore-vs-convert.md   # 还原 vs 直接转换的实测对比
```

把**整个目录**放进你的 skills 根目录下，路径必须形如：

```
<你的 workspace>/.user_skills/pixel-art-restore/
```

落位后的正确结构是 `.../.user_skills/pixel-art-restore/SKILL.md`。

常见错误：解压后多套了一层，变成 `pixel-art-restore/pixel-art-restore/SKILL.md` —— 这样技能永远加载不到，请核对。

## 2. 装依赖

```
pip install proper-pixel-art
```

会自动带上 `numpy / opencv-python-headless / pillow / pyyaml / scipy / av / tqdm`。

- Python 版本 **≥ 3.9**（3.13 实测可用）
- 只有需要处理**视频或 GIF** 输入时才另外需要 `ffmpeg`，纯图片流程不需要
- 全部本地运行，不调 API、不下载模型、不需要联网

## 3. 验装

```
python scripts/measure_grid.py <任意像素风图片>
```

能打印出「唯一颜色 / 相邻色差 / 判定」这几行，说明脚本和 Pillow、numpy 都正常。

再确认命令行入口：

```
ppa --help
```

能打出一屏参数说明即可。若报「找不到 ppa」，说明 Python 的 Scripts 目录不在 PATH 上（Linux 用 `pip install --user` 时常见）——把 `~/.local/bin` 加进 PATH，或改用完整路径调用。

## 4. 使用时注意（这两条已写进 SKILL.md 的「常见坑」，别绕开）

- **先体检再还原。** 对一张图先跑 `scripts/measure_grid.py`。ppa 假设输入被放大了，对已经是 1px 真分辨率的图会过度缩小（实测 131×159 的成品会被压成 9×10，直接报废）。
- **不要用 ppa 的 `-t`。** 软边源图会产出粉灰交错的噪点底；用 `--no-transparent` 出实底，再用 `scripts/key_bg.py` 抠背景。

---

## 快速上手

```bash
# 1) 体检：判断这张图该怎么处理
python scripts/measure_grid.py sprite.png

# 2) 还原：让 ppa 自己检测像素网格
ppa sprite.png -o sprite_true.png --no-transparent

# 3) 去背 + 出 8 倍预览
python scripts/key_bg.py sprite_true.png -o sprite_keyed.png --tol 42 --scale 8 --purge-bg

# 4) 批量处理一个文件夹
python scripts/batch_restore.py ./input ./output --scale 8
```

## 技能适用场景

- AI 出图/截图/网图看着像像素画，但格子不齐、边缘发虚、分辨率虚高
- 想把这类图变成游戏可用的像素素材（sprite、道具、UI 图标）
- 需要判断「直接降采样转像素画」和「还原原网格」该走哪条
- 需要批量还原一批同源素材

## 落位后向维护者回报

装好后请回报一行实际路径，例如 `.../.user_skills/pixel-art-restore/`，方便核对结构。
