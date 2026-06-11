# 手写数字识别 Digit Lab

这是一个 Python 课程设计项目：用户在浏览器画布中手写数字，系统使用 PyTorch CNN 模型实时输出 0-9 的概率分布。游客可直接试用识别功能，登录用户会保存识别历史。

## 功能

- 游客试用识别，用户注册、登录、退出
- Canvas 手写输入，实时识别数字
- 右侧柱形图展示 0-9 softmax 概率
- SQLite 保存用户识别历史
- 关于页面说明项目背景、环境、依赖和模型来源
- 提供训练脚本，可重新训练 MNIST CNN 权重

## 快速启动

建议使用 conda 环境运行。若本机已有 `mnist-torch` 这类 PyTorch 环境，也可以直接复用。

```powershell
conda env create -f environment.yml
conda activate digit-lab
python train.py
python app.py
```

如果使用已有 conda 环境：

```powershell
conda activate mnist-torch
python -m pip install -r requirements.txt
python app.py
```

浏览器打开 `http://127.0.0.1:5001` 即可进入识别台。注册并登录后，识别结果会保存到历史记录。

如果仓库已经包含 `artifacts/digit_cnn.pt`，可以跳过 `python train.py` 直接运行 `python app.py`。若根目录存在 `train.csv` 和 `test.csv`，训练脚本会优先使用本地 CSV；否则通过 torchvision 下载 MNIST。

## 代码结构

```text
app.py                  Flask 应用入口
train.py                MNIST 训练脚本
digit_recognizer/       模型、推理、数据库、认证模块
templates/              Flask 页面模板
static/                 CSS 和 Canvas 前端逻辑
docs/                   说明文档、AI 使用说明和对话 log
environment.yml         conda 环境配置
```

## 模型说明

模型为自行编写的轻量 CNN：

- 输入：`1 x 28 x 28` 灰度图
- 卷积层：`Conv2d(1, 32)`、`Conv2d(32, 64)`
- 分类层：`Linear(64*7*7, 128)`、`Linear(128, 10)`
- 损失函数：交叉熵
- 优化器：Adam
- 数据集：优先使用根目录 `train.csv`、`test.csv`；缺失时通过 `torchvision.datasets.MNIST` 自动下载

## AI 辅助说明

本项目使用 Codex 辅助生成项目结构、部分 Flask 路由、Canvas 交互代码、训练脚本和文档草稿。详细说明见 `docs/AI_USAGE.md` 与 `docs/ai_conversation_log.md`。
