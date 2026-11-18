---
name: rembg-cutout
description: "用 rembg（ONNX 深度学习分割）把图片主体从背景中分离，输出干净透明底 PNG。用于人物/角色/商品/物体去背、抠出发丝与褶边等细碎轮廓、为像素画/立绘/贴纸/游戏 sprite 准备透明底素材。触发词：抠图、去背、抠透明底、去掉背景、remove background、cutout、matting、主体分离；也用于像素化前先在高清图上抠图（先抠图再像素化，不要先像素化再手工抠）。"
license: MIT
metadata:
  version: "1.0"
  author: Luca-42
---

# rembg 抠图去背

## Overview

rembg 是开源 AI 背景移除工具：用 ONNX 分割模型预测前景/背景像素，生成 alpha 蒙版，输出 RGBA 透明图。本技能沉淀环境部署、模型选型、下载排障、抠图参数与验收流程。

**核心原则：先在高清原图上抠图，再做后续风格化。** 不要先把图像素化/缩小再手工抠——降采样减色后主体与背景颜色混在一起，边缘无法分辨，只会留下残边或啃掉主体。

## 环境部署

优先用独立 conda/venv 环境，不污染 base。模型权重通过环境变量指到数据盘，避免占 C 盘。

### 1. 建环境（以 conda 为例）

```bash
conda create -y -p D:\pyenv\rembg python=3.11
```

- Python 3.11 兼容性最稳；3.13 可用但部分依赖轮子可能缺失。
- 环境目录按用户既有约定放置（如 `D:\pyenv\<name>`）。

### 2. 安装包（用国内镜像）

```bash
D:\pyenv\rembg\python.exe -m pip install rembg onnxruntime \
  -i https://mirrors.huaweicloud.com/repository/pypi/simple
```

- `onnxruntime` 为 CPU 推理后端；要 GPU 加速另装 `onnxruntime-gpu` 并匹配 CUDA/cuDNN。
- 连带依赖：numpy、pillow、scipy、pymatting、scikit-image、pooch、numba/llvmlite、jsonschema 等，pip 自动拉取。

### 3. 模型目录（指到数据盘）

设置环境变量 `REMBG_HOME`（旧名 `U2NET_HOME` 仍兼容），模型落在 `<REMBG_HOME>/models/<模型名>/*.onnx`：

```powershell
$env:REMBG_HOME = "D:\画画\rembg-models"
```

- 进程内临时设置即可；要长期生效再写进系统/用户环境变量。
- 模型只在首次调用对应模型时下载一次，之后离线可用。

## 模型选型

| 模型 | 适用 | 备注 |
|---|---|---|
| `isnet-anime` | **二次元/动漫角色**（头发、头饰、翅膀、褶边） | 动漫图首选；本技能默认 |
| `u2net` | 通用人物/物体 | 最常用的通用基线 |
| `isnet-general-use` | 通用实景物体 | 非动漫通用 |
| `birefnet-general` | 高精度通用 | 体积大、推理慢 |
| `birefnet-portrait` | 人像特写 | 真人头像 |
| `silueta` | 轻量通用 | 体积小、精度一般 |

判断：二次元角色用 `isnet-anime`；真人/商品/实景用 `u2net` 或 `isnet-general-use`；要求高精度再上 birefnet。

## 下载与排障

模型从 GitHub Releases 下载，国内直连常被重置（`ConnectionResetError 10054`）或 SSL 证书校验失败（`SSLCertVerificationError`）。

1. **pip 包不需要梯子**，走国内镜像即可。
2. **模型权重直连不稳**，二选一：
   - 开梯子让 rembg 自动下载；
   - 走 GitHub 代理镜像手动下载，放入 `<REMBG_HOME>/models/<模型名>/<模型名>.onnx`，文件名与模型名一致。
3. 镜像示例（按需替换模型名与版本）：
   ```
   https://gh-proxy.com/https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-anime.onnx
   ```
4. **校验完整性**：rembg 按 MD5 校验，残包会重新下载。手动下载后用 `Get-FileHash <file> -Algorithm MD5` 比对官方记录值；不匹配说明文件被截断，需重下。
5. 若 `new_session` 后 `remove()` 报 `'str' object has no attribute 'predict'`：`session` 参数要传会话对象，模型名只能传给 `new_session()`，不能直接传给 `remove()`。

## 抠图流程

### 1. 预处理（可选但推荐）

- 裁掉水印、弹幕、播放控件、界面按钮、无关人物剪影等干扰元素；这些会被模型误判为前景。
- 不要预先锐化、放大或重调色，避免破坏主体边缘判断。

### 2. 调用抠图

```python
from rembg import remove, new_session
from PIL import Image

session = new_session("isnet-anime")          # 模型名在这里传
im = Image.open("input.png")
out = remove(im, session=session)             # 会话对象在这里传
out.save("cutout.png")                        # RGBA 透明底
```

### 3. 常用参数（`remove()`）

| 参数 | 默认 | 说明 |
|---|---|---|
| `alpha_matting` | `False` | 开启 alpha 蒙版细化；软边发丝更细，但软边源图易出半透明噪点 |
| `alpha_matting_foreground_threshold` | 240 | 前景阈值（matting 开启时生效） |
| `alpha_matting_background_threshold` | 10 | 背景阈值 |
| `alpha_matting_erode_size` | 10 | 边缘腐蚀像素数 |
| `post_process_mask` | `False` | 对蒙版做后处理清理 |
| `decontaminate` | `False` | 去除软边上的背景色溢色（matting 开启时忽略） |

- 默认二值硬蒙版多数场景够用；边缘发虚时再试 `alpha_matting=True`。
- 开 matting 后若出现粉灰半透明噪点底，关闭 matting 改用二值蒙版。

### 4. 残边与误判处理

- **背景色溢边**：开 `decontaminate=True`；或在透明图上清理紧邻透明区的浅色残边像素。
- **场景元素被误判为前景**（栏杆、桌面、剪影）：模型无法识别时，最干净的做法是裁到不含该元素的构图（如胸像），不要硬擦——颜色与主体接近时阈值分离会啃掉身体。
- **孤立散点**：按四/八邻域连通域清掉 ≤3px 的孤立块；保留角色自身小结构（眼睛高光、蝴蝶结、呆毛断裂段）。

## 验收清单

1. 输出为 RGBA；alpha 呈透明/不透明双峰，无大片半透明混色。
2. 主体轮廓完整：发丝、褶边、头饰、翅膀等细碎结构未被啃掉。
3. 背景连通域已透明，无成片背景块、光粒、控件残留。
4. 轮廓外无孤立散点（角色自身小高光除外）。
5. 灰底预览下边缘干净，无浅色晕边。

## 与像素化衔接

抠出的高清透明主体交给像素化流程（见 `pixel-art-restore` 技能）：
1. 高清透明 PNG → 轻度高斯模糊 → 降采样到目标长边（128/160px）→ dominant 取色减色、不抖动；
2. alpha 通道用最近邻降采样保硬边，不要用平滑重采样；
3. 像素阶段只做轻量散点清理，不承担主要抠图工作。

## 脚本

- `scripts/cutout.py`：命令行批量抠图，支持选模型、matting、后处理、透明 PNG 与灰底预览输出。
- 环境部署与模型下载排障细节见 `references/setup-and-troubleshooting.md`。
