# 手写数字识别项目说明文档

## 1. 项目概述

本项目实现了一个基于 Web 的手写数字识别系统。用户可直接以游客身份在左侧黑色画布中用鼠标手写数字，系统实时将画布内容转换为 28x28 灰度图，并使用 PyTorch 卷积神经网络预测 0-9 的概率分布。右侧柱形图实时展示每个数字的预测概率；注册并登录后，历史页面会保存当前用户的识别记录。

## 2. 模块功能简图

```text
用户浏览器
  ├─ 登录/注册页面
  ├─ Canvas 手写画布
  └─ 概率柱形图
        │ POST /api/predict
        ▼
Flask 后端
  ├─ 用户认证
  ├─ SQLite 历史记录
  └─ PyTorch CNN 推理
        ▲
        │ artifacts/digit_cnn.pt
train.py 训练脚本 ← MNIST 数据集
```

## 3. 关键技术选型

- Python 3.12：项目主要开发语言。
- Flask 3.1：提供 Web 页面、登录注册和推理 API。
- PyTorch 2.5：编写 CNN 模型、训练和推理流程。
- torchvision：当本地 CSV 数据不存在时，自动下载 MNIST 数据集。
- SQLite：保存用户、密码哈希和识别历史。
- HTML Canvas：实现浏览器端手写输入。

模型使用自行编写的 `DigitCNN`，包含两组卷积、池化和全连接层。训练脚本优先读取根目录 `train.csv` 和 `test.csv`，格式为第一列标签、后 784 列像素；若本地 CSV 不存在，则通过 torchvision 下载 MNIST。训练使用交叉熵损失和 Adam 优化器，完成后保存权重。

## 4. 特色功能实现原理

实时识别的关键在于前端节流推理。用户拖动鼠标时，Canvas 绘制白色笔迹；JavaScript 每隔约 110ms 将当前画布缩放到 28x28，并读取灰度像素数组。后端收到数组后按 MNIST 的均值和标准差归一化，送入 CNN 得到 logits，再用 softmax 转换为概率。前端根据返回概率更新 0-9 的柱形图，并突出最高概率数字。

用户系统采用 SQLite。本地注册时保存用户名、随机盐和 PBKDF2 密码哈希，不保存明文密码。游客模式只进行实时推理，不写入历史；登录后每次推理会保存预测数字、概率分布、缩略图和时间戳，历史页面按登录用户隔离展示。

## 5. 开发环境与运行指南

建议环境：Windows 11，conda，Python 3.10 或 3.12。

```powershell
conda env create -f environment.yml
conda activate digit-lab
python train.py
python app.py
```

访问 `http://127.0.0.1:5001` 即可试用识别功能；注册登录后可保存历史记录。若已经提供 `artifacts/digit_cnn.pt`，可跳过训练步骤。

## 6. 借鉴资源及个人贡献说明

数据集来源为 MNIST，通过 torchvision 自动下载。项目没有使用现成手写数字识别成品，仅参考课程要求完成技术选型。AI 工具 OpenAI Codex 辅助生成了项目骨架、部分代码和文档草稿，具体范围见 `docs/AI_USAGE.md` 与 `docs/ai_conversation_log.md`。个人贡献包括需求确认、技术路线选择、代码调试、模型训练、运行测试和最终文档整理。
