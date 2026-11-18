#!/usr/bin/env python3
"""批量还原: 对一个文件夹里的图片逐张跑 proper-pixel-art, 再统一去背出预览。

用法:
    python batch_restore.py <输入文件夹> <输出文件夹> [--width 64] [--tol 42]
                            [--scale 8] [--keep-bg] [--recursive]

依赖: 已安装 proper-pixel-art(pip install proper-pixel-art), 且 ppa 在 PATH 上。
"""
import argparse
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from key_bg import flood_key, drop_isolated, trim, preview  # noqa: E402

EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def run_ppa(src, dst, width):
    cmd = ["ppa", src, "-o", dst, "--no-transparent"]
    if width:
        cmd += ["-w", str(width)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  [失败] %s\n  %s" % (os.path.basename(src), (r.stderr or r.stdout).strip()[:200]))
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--width", type=int, help="强制指定真实像素宽度(源图像的像素格边长); 省略则自动检测")
    ap.add_argument("--tol", type=int, default=42)
    ap.add_argument("--scale", type=int, default=8)
    ap.add_argument("--keep-bg", action="store_true", help="不去背")
    ap.add_argument("--recursive", action="store_true")
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    files = []
    if a.recursive:
        for root, _, names in os.walk(a.src_dir):
            files += [os.path.join(root, n) for n in names if n.lower().endswith(EXTS)]
    else:
        files = [os.path.join(a.src_dir, n) for n in os.listdir(a.src_dir) if n.lower().endswith(EXTS)]

    ok = 0
    for f in sorted(files):
        stem = os.path.splitext(os.path.basename(f))[0]
        raw = os.path.join(a.out_dir, stem + "_true.png")
        print("[还原]", os.path.basename(f))
        if not run_ppa(f, raw, a.width):
            continue
        if a.keep_bg:
            ok += 1
            continue
        keyed = trim(drop_isolated(flood_key(Image.open(raw), a.tol)))
        keyed.save(raw)
        preview(keyed, a.scale).save(os.path.join(a.out_dir, "%s_x%d.png" % (stem, a.scale)))
        print("   -> %dx%d" % keyed.size)
        ok += 1

    print("完成: %d/%d 张" % (ok, len(files)))


if __name__ == "__main__":
    main()
