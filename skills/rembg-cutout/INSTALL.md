# rembg-cutout 安装说明

本目录是 skill 包 `rembg-cutout`，作用是**用 rembg（ONNX 深度学习分割）在高清图上 AI 抠图去背，输出透明底 PNG**。它是像素化前的准备步骤，配合 `pixel-art-restore` 使用。

---

## 1. 落位（不要改名、不要拆散文件）

目录 `rembg-cutout/` 内含：

```
rembg-cutout/
├── SKILL.md                              # 技能定义、模型选型、参数与验收
├── INSTALL.md                            # 本文件
├── scripts/
│   └── cutout.py                         # 命令行批量抠图：选模型 / matting / 预览
└── references/
    └── setup-and-troubleshooting.md      # 环境部署、模型清单、报错排障
```

把**整个目录**放进你的 skills 根目录下：

```
<你的 workspace>/.user_skills/rembg-cutout/
```

落位后的正确结构是 `.../.user_skills/rembg-cutout/SKILL.md`。多套一层（`rembg-cutout/rembg-cutout/SKILL.md`）会导致技能加载不到。

## 2. 环境建议

用独立 conda/venv 环境，不污染 base。Python 3.11 兼容性最稳：

```bash
conda create -y -p D:\pyenv\rembg python=3.11
```

## 3. 装依赖（走国内镜像）

```bash
D:\pyenv\rembg\python.exe -m pip install rembg onnxruntime \
  -i https://mirrors.huaweicloud.com/repository/pypi/simple
```

- `onnxruntime` 为 CPU 推理后端；要 GPU 加速另装 `onnxruntime-gpu` 并匹配 CUDA/cuDNN。
- 连带依赖（numpy、pillow、scipy、pymatting、scikit-image、pooch、numba/llvmlite 等）由 pip 自动拉取。

## 4. 模型目录（指到数据盘，避免占 C 盘）

设置环境变量 `REMBG_HOME`（旧名 `U2NET_HOME` 兼容），模型落在 `<REMBG_HOME>/models/<模型名>/*.onnx`：

```powershell
$env:REMBG_HOME = "D:\画画\rembg-models"
```

## 5. 模型选择

| 模型 | 适用 |
|---|---|
| `isnet-anime` | 二次元/动漫角色（头发、头饰、翅膀、褶边），默认 |
| `u2net` | 通用人物/物体 |
| `isnet-general-use` | 通用实景物体 |
| `birefnet-general` / `birefnet-portrait` | 高精度通用 / 人像特写 |
| `silueta` | 轻量通用 |

## 6. 网络与下载

- **pip 包不需要梯子**，走国内镜像即可。
- **模型权重**从 GitHub Releases 下载，国内直连常被重置（`10054`）或 SSL 校验失败。二选一：
  - 开梯子让 rembg 自动下载；
  - 走 GitHub 代理镜像手动下载，放入 `<REMBG_HOME>/models/<模型名>/<模型名>.onnx`，文件名与模型名一致。
- 手动下载后用 `Get-FileHash <file> -Algorithm MD5` 比对官方 MD5；不匹配说明被截断，需重下。

## 7. 快速上手

```bash
# 单张：动漫角色，后处理清理蒙版，6 倍灰底预览
python scripts/cutout.py char.png -o out --model isnet-anime --post-process

# 整个文件夹
python scripts/cutout.py ./photos -o out --model u2net --scale 4
```

参数：`--matting` 细化软边、`--decontaminate` 去背景色溢边、`--scale` 预览倍数。详见 `references/setup-and-troubleshooting.md`。

## 8. 与像素化衔接

抠出的高清透明主体交给 `pixel-art-restore`：

1. 高清透明 PNG → 轻度高斯模糊 → 降采样到目标长边（128/160px）→ dominant 取色减色、不抖动；
2. alpha 通道用最近邻降采样保硬边，不要用平滑重采样；
3. 像素阶段只做轻量散点清理，不承担主要抠图工作。
