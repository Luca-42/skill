#!/usr/bin/env python3
"""rembg 抠图去背：输入图片，输出透明底 PNG + 灰底放大预览。

用法:
    python cutout.py <输入图片或文件夹> -o <输出目录> [--model isnet-anime]
                     [--matting] [--post-process] [--decontaminate] [--scale 6]

示例:
    python cutout.py char.png -o out --model isnet-anime
    python cutout.py ./photos -o out --model u2net --matting --scale 4

说明:
- 模型名传给 new_session(); remove() 的 session 参数接收会话对象。
- 模型权重目录由环境变量 REMBG_HOME(或 U2NET_HOME) 指定, 首次调用自动下载。
- 透明输出为 RGBA; 预览为灰底最近邻放大, 便于检查边缘与残边。
"""
import argparse
import os
import sys
from pathlib import Path

from PIL import Image


def cut_one(src: Path, out_dir: Path, model: str, matting: bool,
            post_process: bool, decontaminate: bool, scale: int,
            fg: int, bg: int, erode: int) -> None:
    from rembg import remove, new_session

    session = new_session(model)
    im = Image.open(src)
    out = remove(
        im,
        session=session,
        alpha_matting=matting,
        alpha_matting_foreground_threshold=fg,
        alpha_matting_background_threshold=bg,
        alpha_matting_erode_size=erode,
        post_process_mask=post_process,
        decontaminate=decontaminate,
    )
    out = out.convert("RGBA")

    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{src.stem}.png"
    out.save(png)

    # 灰底最近邻放大预览
    prev = out.resize((out.size[0] * scale, out.size[1] * scale), Image.NEAREST)
    bg_img = Image.new("RGBA", prev.size, (58, 58, 64, 255))
    Image.alpha_composite(bg_img, prev).convert("RGB").save(
        out_dir / f"{src.stem}_x{scale}.png"
    )

    alpha = out.getchannel("A")
    opaque = sum(1 for v in alpha.getdata() if v > 0)
    print(f"[OK] {src.name} -> {png.name}  尺寸 {out.size}  不透明像素 {opaque}")


def main() -> None:
    ap = argparse.ArgumentParser(description="rembg 抠图去背")
    ap.add_argument("input", help="输入图片路径或文件夹")
    ap.add_argument("-o", "--out", required=True, help="输出目录")
    ap.add_argument("--model", default="isnet-anime",
                    help="模型名: isnet-anime/u2net/isnet-general-use/"
                         "birefnet-general/birefnet-portrait/silueta (默认 isnet-anime)")
    ap.add_argument("--matting", action="store_true", help="开启 alpha matting 细化软边")
    ap.add_argument("--post-process", action="store_true", help="后处理清理蒙版")
    ap.add_argument("--decontaminate", action="store_true", help="去除背景色溢边")
    ap.add_argument("--scale", type=int, default=6, help="预览放大倍数 (默认 6)")
    ap.add_argument("--fg", type=int, default=240, help="matting 前景阈值")
    ap.add_argument("--bg", type=int, default=10, help="matting 背景阈值")
    ap.add_argument("--erode", type=int, default=10, help="matting 边缘腐蚀像素数")
    a = ap.parse_args()

    src = Path(a.input)
    out_dir = Path(a.out)
    if src.is_dir():
        files = [p for p in src.iterdir()
                 if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp")]
    else:
        files = [src]

    if not files:
        sys.exit("未找到可处理的图片")

    for f in files:
        cut_one(f, out_dir, a.model, a.matting, a.post_process,
                a.decontaminate, a.scale, a.fg, a.bg, a.erode)


if __name__ == "__main__":
    main()
