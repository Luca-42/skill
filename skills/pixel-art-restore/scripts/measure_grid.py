#!/usr/bin/env python3
"""给一张"疑似像素画"做体检, 决定该走还原还是走转换。

用法:
    python measure_grid.py <image> [--thr 26]

输出四组指标 + 一句建议。指标不是判决书: 它们只帮你选路线, 真正靠谱的验证是
跑一次 ppa 看它检测出的像素宽和输出尺寸是否合理。

指标含义(基于实测样本):
  uniq   唯一颜色数         软边 AI 图 ~十几万; 成型像素画 <2000
  grad   相邻像素平均色差   软边 ~4; 硬边像素画 ~10-20
  eq     横向相邻像素完全相同的比例   1px 精细像素画 ~0.5; 有平涂色块(被放大 N 倍) ~0.8+
  gap    扫描线上颜色突变的间距分布   间距集中在某值 -> 网格整齐

四条典型判据:
  uniq>50000 & grad<8   -> 软边(生成模型的伪像素/插画), 走 ppa 还原
  uniq<=2000 & grad>=10 & eq<0.7 -> 已是 1px 真像素画, 不用还原
  uniq<=2000 & eq>=0.7  -> 色块化像素画, 可能被放大了约 1/(1-eq) 倍
  其它                   -> 中间态, 直接让 ppa 自动检测再人工看一眼
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image


def gap_stats(arr, thr, max_gap):
    """逐行找颜色突变的位置, 统计相邻突变的间距"""
    gaps = []
    h, w, _ = arr.shape
    for y in range(h):
        row = arr[y]
        diff = np.abs(np.diff(row, axis=0)).sum(1)
        idx = np.where(diff > thr)[0]
        if len(idx) < 2:
            continue
        d = np.diff(idx)
        gaps.extend([int(v) for v in d if 4 <= v <= max_gap])
    if not gaps:
        return None, None, None
    g = np.array(gaps)
    mode = int(np.bincount(g).argmax())
    stable = float(np.mean(np.abs(g - mode) <= 1))
    return int(np.median(g)), mode, stable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--thr", type=int, default=26, help="颜色突变阈值(通道差之和), 默认 26")
    a = ap.parse_args()

    if not os.path.exists(a.image):
        sys.exit("找不到文件: %s" % a.image)

    im = Image.open(a.image).convert("RGB")
    arr = np.asarray(im).astype(np.int16)
    h, w, _ = arr.shape

    eq = float((arr[:, 1:] == arr[:, :-1]).all(2).mean())
    uniq = int(len(np.unique(arr.reshape(-1, 3), axis=0)))
    grad = float(np.abs(np.diff(arr, axis=1)).mean())
    med, mode, stable = gap_stats(arr, a.thr, 60)

    print("尺寸: %dx%d" % (w, h))
    print("唯一颜色: %d" % uniq)
    print("相邻色差(平均): %.2f" % grad)
    print("横向完全相同比例: %.2f" % eq)
    if med is None:
        print("间距: 没测到足够的突变点(图太平或阈值太高, 试 --thr 12)")
    else:
        print("间距: 中位=%d 众数=%d 落在众数±1的比例=%.0f%%" % (med, mode, stable * 100))

    print()
    if uniq > 50000 and grad < 8:
        print("判定: 软边图像(生成模型的伪像素或普通插画)")
        print("动作: 是像素画意图 -> ppa <img> -o out.png --no-transparent")
        print("      是照片/实拍 -> 别用还原, 走降采样+减色(见 references/conversion-vs-restore.md)")
    elif uniq <= 2000 and grad >= 10 and not (eq >= 0.7 and w > 400):
        print("判定: 已经是 1px 真像素画")
        print("动作: 不需要还原, 直接用; 要缩小就用整数倍最近邻")
    elif uniq <= 2000 and eq >= 0.7 and w > 400:
        n = max(2, round(1 / max(1e-6, 1 - eq)))
        print("判定: 色块化像素画, 疑似被放大了约 %d 倍" % n)
        print("动作: ppa <img> -o out.png -w %d --no-transparent   (或直接用最近邻缩小 %d 倍)" % (n, n))
    else:
        print("判定: 中间态, 判据不足以自动决策")
        print("动作: ppa <img> -o out.png --no-transparent, 然后看输出的宽度是否接近预期")


if __name__ == "__main__":
    main()
