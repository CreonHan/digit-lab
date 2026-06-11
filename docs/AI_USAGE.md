# AI 辅助编程说明

## 使用工具

- AI 工具：OpenAI Codex
- 使用时间：2026 年 6 月
- 辅助范围：需求拆解、项目结构设计、Flask 路由、SQLite 数据层、PyTorch CNN 模型代码、Canvas 实时绘图交互、README 和说明文档草稿。

## AI 辅助生成的主要代码段

1. `app.py`
   - Flask 应用初始化
   - 注册、登录、退出、识别台、历史记录、关于页面路由
   - `/api/predict` 推理接口

2. `digit_recognizer/model.py`
   - `DigitCNN` 卷积神经网络结构

3. `train.py`
   - MNIST 数据加载
   - 训练循环、验证准确率计算、模型权重保存

4. `static/js/draw.js`
   - Canvas 鼠标/触控绘制
   - 28x28 灰度图采样
   - 实时请求后端推理接口并更新概率条形图

5. `templates/` 与 `static/css/styles.css`
   - 登录、注册、识别、历史、关于页面
   - 页面布局和视觉样式

## 个人修改与理解

开发者负责确认课程要求、确定项目主题、选择 Web UI + PyTorch CNN 技术路线，并根据课程提交要求整理文档、运行测试、训练模型。AI 输出作为辅助草稿，最终代码需要由开发者阅读、调试和确认。
