#!/usr/bin/env python3
"""给已还原的像素图做干净去背 + 清理散点 + 出放大预览。

为什么需要它: proper-pixel-art 自带的 -t/--transparent 在软边源图上会产出
粉灰交错的半透明噪点底, 不能直接用。这里用"从边框洪水填充"的方式抠底,
结果边缘干净、无半透明过渡。

用法:
    python key_bg.py restored.png -o out.png [--tol 42] [--scale 8]
                                 [--bg 255,255,255] [--keep-specks] [--no-trim]
"""
import argparse
import math
import os
import sys

from PIL import Image


def color_dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def flood_key(im, tol, bg=None):
    """从边框向内洪水填充, 把与背景色接近的连通区域变透明"""
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    ref = bg if bg else px[0, 0]

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            opx[x, y] = (c[0], c[1], c[2], 255)

    seen = [[False] * w for _ in range(h)]
    stack = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    stack += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
            continue
        if color_dist(px[x, y], ref) > tol:
            continue
        seen[y][x] = True
        opx[x, y] = (0, 0, 0, 0)
        stack.append((x - 1, y))
        stack.append((x + 1, y))
        stack.append((x, y - 1))
        stack.append((x, y + 1))
    return out


def clean_rim(img, ref, tol, passes=2):
    """清理沿透明边界残留的浅色描边像素(源图软边被放大后留下的浅色晕)

    只在"紧邻透明区、且颜色仍接近背景色"的像素上动作, 不会啃掉主体。
    """
    w, h = img.size
    px = img.load()
    limit = tol * 1.6
    for _ in range(passes):
        changed = 0
        for y in range(h):
            for x in range(w):
                p = px[x, y]
                if p[3] == 0:
                    continue
                touches = False
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                        touches = True
                        break
                if touches and color_dist(p[:3], ref) <= limit:
                    px[x, y] = (0, 0, 0, 0)
                    changed += 1
        if not changed:
            break
    return img


def purge_bg(img, ref, tol):
    """把画面上任何位置与背景色接近的像素变透明(用于清理被围住的背景残留)"""
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if p[3] and color_dist(p[:3], ref) <= tol:
                px[x, y] = (0, 0, 0, 0)
    return img


def drop_isolated(img):
    """删掉四周没有邻居的孤立不透明像素(描边外的散点)"""
    w, h = img.size
    px = img.load()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if px[x, y][3] == 0:
                continue
            n = sum(1 for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                    if px[nx, ny][3] > 0)
            if n == 0:
                px[x, y] = (0, 0, 0, 0)
    return img


def trim(img):
    box = img.getbbox()
    return img.crop(box) if box else img


def preview(img, scale, bgc=(58, 58, 64)):
    p = img.resize((img.size[0] * scale, img.size[1] * scale), Image.NEAREST)
    s = Image.new("RGB", p.size, bgc)
    s.paste(p, (0, 0), p)
    return s


def parse_color(s):
    parts = [int(v) for v in s.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("颜色要写成 R,G,B")
    return tuple(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("-o", "--out", required=True, help="透明底 PNG 输出路径")
    ap.add_argument("--tol", type=int, default=42, help="背景色容差(RGB 欧氏距离), 默认 42")
    ap.add_argument("--bg", type=parse_color, help="指定背景色 R,G,B; 默认取左上角像素")
    ap.add_argument("--scale", type=int, default=8, help="预览放大倍数, 默认 8")
    ap.add_argument("--preview", help="预览输出路径, 默认 <out>_x<scale>.png")
    ap.add_argument("--keep-specks", action="store_true", help="保留孤立散点")
    ap.add_argument("--no-rim", action="store_true", help="不做边缘浅色残边清理")
    ap.add_argument("--purge-bg", action="store_true",
                    help="把画面上任何位置接近背景色的像素也变透明(清理被围住的背景残留)")
    ap.add_argument("--no-trim", action="store_true", help="不裁掉四周透明留白")
    a = ap.parse_args()

    if not os.path.exists(a.image):
        sys.exit("找不到文件: %s" % a.image)

    src = Image.open(a.image)
    ref = a.bg if a.bg else src.convert("RGB").getpixel((0, 0))
    keyed = flood_key(src, a.tol, ref)
    if not a.no_rim:
        keyed = clean_rim(keyed, ref, a.tol)
    if a.purge_bg:
        keyed = purge_bg(keyed, ref, a.tol)
    if not a.keep_specks:
        keyed = drop_isolated(keyed)
    if not a.no_trim:
        keyed = trim(keyed)
    keyed.save(a.out)

    prev_path = a.preview or os.path.join(
        os.path.dirname(a.out), os.path.splitext(os.path.basename(a.out))[0] + "_x%d.png" % a.scale)
    preview(keyed, a.scale).save(prev_path)

    opaque = sum(1 for p in keyed.getdata() if p[3] > 0)
    print("输出: %s  尺寸: %dx%d  不透明像素: %d" % (a.out, keyed.size[0], keyed.size[1], opaque))
    print("预览: %s" % prev_path)


if __name__ == "__main__":
    main()
