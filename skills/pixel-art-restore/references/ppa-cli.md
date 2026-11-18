# proper-pixel-art (ppa) 命令行参考

包名 `proper-pixel-art`，版本 2.0.0，MIT。命令行入口是 **`ppa`**（不是 `python -m proper_pixel_art`，该包没有 `__main__`，那样调用会报 "No module named proper_pixel_art.__main__"）。

## 基本用法

```bash
ppa <输入> [-o 输出] [选项]
```

`-o` 可以给目录也可以给文件路径；省略时输出到当前目录。输入支持图片、视频、GIF，后两者自动走视频管线。

## 参数

| 参数 | 说明 |
|---|---|
| `-o, --output` | 输出路径（目录或文件） |
| `--config` | YAML 配置文件；命令行显式参数会覆盖文件里的值 |
| `--intermediate-dir` | 保存算法中间步骤的可视化图，调参时用；正常流程不需要 |
| `--color-method {dominant,palette}` | 取色方式。`dominant`（默认）保留原色；`palette` 量化到固定调色板 |
| `-c, --colors N` | 调色板色数 1–256，隐含 `--color-method palette` |
| `-s, --scale-result N` | 输出放大 N 倍（每像素变 N×N 块），只影响显示，不改变真实分辨率 |
| `-t, --transparent / --no-transparent` | 透明背景下输出。**软边源图上不可用**，见下方"已知行为" |
| `-w, --pixel-width N` | 源图里一个像素格的边长（px）。省略则自动检测 |
| `-u, --initial-upscale N` | 网格检测前的初始放大倍数。检测到的间距过大时调大它 |
| `-f, --format {mp4,gif}` | 视频/GIF 输出格式，仅对视频输入生效 |
| `-n, --sample-frames N` | 视频抽帧数量用于网格检测，默认 8 |

另有 `ppa web` 启动浏览器 UI（本地交互调参）。

## 已知行为（实测）

- **自动检测格宽**：983px 宽、格≈7.5px 的源图 → 输出 131×159。对软边但确有周期的 AI 图，检测是可靠的，通常优于手填 `-w`。
- **对已经是 1:1 的像素画会过度缩小**：把 131×159 的成品再喂进去，输出 9×10，直接报废。它默认假设"输入是被放大的"，不做"是否已 1:1"的判断。
- **`-t` 产出粉灰交错噪点底**：软边 + 背景色接近主体时，半透明像素带噪。改用 `--no-transparent` 出实底，再用本技能的 `scripts/key_bg.py` 洪水填充抠图。
- **`palette` 模式改色是设计如此**：调色板覆盖不到主体色域时会明显偏色（例如浅蓝主体在 PICO-8 16 色下变灰紫）。做还原用默认 `dominant`。
- **黑描边散点**：源图描边如果断断续续，还原后轮廓外会留零星黑点，脚本能清掉大部分四邻域孤点，成片的要手擦。
- 输出默认 PNG；透明输出时是 RGBA。

## 依赖

`av, numpy, opencv-python-headless, pillow, pyyaml, scipy, tqdm`（pip 自动装齐）。视频/GIF 输入另需系统里有 ffmpeg。

Python 3.13 实测可用。
