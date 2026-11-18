# 环境部署与排障参考

## 目录

- [环境搭建步骤](#环境搭建步骤)
- [模型清单与下载地址](#模型清单与下载地址)
- [常见报错与处理](#常见报错与处理)
- [本次实测结论](#本次实测结论)

## 环境搭建步骤

### 1. 独立 conda 环境

```bash
conda create -y -p D:\pyenv\rembg python=3.11
```

- 解释器路径：`D:\pyenv\rembg\python.exe`
- 不要装进 base，避免依赖与其他项目冲突。

### 2. 安装 rembg 与推理后端

```bash
D:\pyenv\rembg\python.exe -m pip install rembg onnxruntime \
  -i https://mirrors.huaweicloud.com/repository/pypi/simple
```

已验证可用版本（实测）：rembg 2.0.87、onnxruntime 1.32.0、numpy 2.4.6、pillow 13.0.0。

### 3. 指定模型目录（数据盘）

```powershell
$env:REMBG_HOME = "D:\画画\rembg-models"
```

目录结构：

```
D:\画画\rembg-models\
└── models\
    └── isnet-anime\
        └── isnet-anime.onnx
```

- `U2NET_HOME` 为旧变量名，仍兼容；`REMBG_HOME` 优先。
- 进程内设置即生效；长期使用再写入用户/系统环境变量。

## 模型清单与下载地址

基础 URL：`https://github.com/danielgatis/rembg/releases/download/v0.0.0/`

| 模型名 | 文件 | 适用 |
|---|---|---|
| `isnet-anime` | `isnet-anime.onnx` | 二次元/动漫角色 |
| `u2net` | `u2net.onnx` | 通用人物/物体 |
| `u2netp` | `u2netp.onnx` | 轻量通用 |
| `isnet-general-use` | `isnet-general-use.onnx` | 通用实景 |
| `silueta` | `silueta.onnx` | 轻量通用 |
| `birefnet-general` | `birefnet-general.onnx` | 高精度通用 |
| `birefnet-portrait` | `birefnet-portrait.onnx` | 人像特写 |

国内下载走代理前缀：

```
https://gh-proxy.com/<原始 GitHub Releases 地址>
```

下载后放入 `<REMBG_HOME>/models/<模型名>/`，文件名与模型名一致。

## 常见报错与处理

### `ConnectionResetError 10054` / 下载中断

GitHub Releases 直连被重置。改用代理镜像手动下载，或开梯子后让 rembg 自动下载。

### `SSLCertVerificationError: certificate verify failed`

本地证书链校验失败。同上走代理镜像；或手动下载模型文件放到模型目录，跳过运行时联网。

### `'str' object has no attribute 'predict'`

调用方式错误：模型名只能传给 `new_session()`，`remove()` 的 `session` 参数要传会话对象。

```python
session = new_session("isnet-anime")   # 模型名在这里
out = remove(im, session=session)      # 会话对象在这里
```

### 模型残包 / MD5 不匹配

中断下载会留下截断的 `.onnx`。rembg 按 MD5 校验，不通过会重新下载；手动放置时先用 `Get-FileHash` 比对官方 MD5，不匹配就删除重下。

### 半透明噪点底（粉灰交错）

开启 alpha matting 后软边源图容易出半透明噪点。关闭 `alpha_matting` 用二值硬蒙版；或检查是否把背景浅色像素误纳入前景。

### 背景元素被保留（栏杆、桌面、剪影）

模型把场景元素误判为前景。颜色与主体接近时阈值分离会啃掉身体，优先裁到不含该元素的构图（胸像/半身），不要硬擦。

## 实测结论

- 流程：裁掉弹幕/控件/剪影 → `isnet-anime` 高清抠图 → 裁去栏杆与下半身 → 降采样减色成像素画。
- 二次元角色用 `isnet-anime`，边缘（头发、头饰、翅膀）分离明显优于通用模型。
- 抠图必须在高清原图上做；先像素化再手工抠会因颜色混合而残边或啃主体。
- 模型 167.91 MB，MD5 `6f184e756bb3bd901c8849220a83e38e`（isnet-anime）。
