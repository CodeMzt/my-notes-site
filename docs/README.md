## 🚀 欢迎来到我的嵌入式与机器学习笔记站

**Mzt2006 的技术备忘录与学习记录**

------

### 👋 关于本站

本网站是我个人在 **嵌入式系统（Embedded Systems）**和 **机器学习（Machine Learning）**领域学习与实践的知识仓库。

内容涵盖从底层硬件架构（ARM 汇编、Cortex-M）到实时操作系统（FreeRTOS），再到上层算法（电控、视觉）的完整技术栈。旨在系统化地整理和回顾复杂的知识点，供自己查阅，也欢迎同行交流。

------

### 📚 主要学习模块

以下是本站最核心的三个知识板块，你可以点击标题进入各领域的深度学习。

| **模块**         | **焦点内容**                                                 | **关键词**                                        |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------- |
| **💻 嵌入式软件** | ARM 架构、RTOS 核心机制、FreeRTOS 源码分析、HAL 库开发、底层通信协议。 | #ARM #FreeRTOS #STM32 #ContextSwitching           |
| **🤖 机器学习**   | Pytorch 框架学习、深度神经网络模型、张量操作、数据处理与可视化。 | #PyTorch #DataScience #NeuralNetwork #Tensorboard |
| **💡 电控与视觉** | PID、LQR、SMC 等经典控制算法，机器视觉基础及嵌入式视觉应用（K230）。 | #ControlAlgos #CV #Robotics                       |

------

### 🎯 快速开始（Quick Start）

#### 实时操作系统 (RTOS)

从 **FreeRTOS** 的核心概念开始，理解多任务环境下的并发和同步机制。

- [FreeRTOS 简介](EmbeddedSoft/RTOS/FreeRTOS/FreeRTOS.md)
- [同步、互斥与通信](EmbeddedSoft/RTOS/FreeRTOS/Sync_Comms.md)
- [任务调度](https://www.google.com/search?q=/EmbeddedSoft/RTOS/FreeRTOS/Scheduling.md)

#### 硬件架构基础

从最底层理解处理器和编程的原理。

- [ARM 架构概述](EmbeddedSoft/ARM_Arch/ARM_Arch.md)
- [汇编语言入门](EmbeddedSoft/Assembly_Intro/Assembly_Intro.md)
- [内存管理](EmbeddedSoft/Assembly_Intro/Mem_Mgmt.md)

#### Pytorch 入门

快速了解 Pytorch 框架的核心组件。

- [Pytorch - 张量](MachineLearning/Pytorch_Learning/tensor.ipynb)
- [Pytorch - 神经网络](MachineLearning/Pytorch_Learning/nn.ipynb)

------

### ✨ 网站特性

- **🌐 中英混合命名:** 文件路径使用英文，确保跨平台部署稳定；标题和内容使用中文，方便阅读。
- **🌙 明暗模式:** 支持一键切换明亮和暗黑模式，适配不同阅读环境。
- **🔍 增强搜索:** 启用搜索建议和高亮功能，帮助快速定位知识点。
- **📄 Jupyter 兼容:** 直接展示 `.ipynb` 笔记内容，方便查阅机器学习实验。

## 🛠️ 本地开发与贡献

### 环境配置

```bash
# 克隆仓库
git clone https://github.com/Mzt2006/tech-notes.git
cd tech-notes

# 安装文档工具（可选）
pip install mkdocs mkdocs-material
```

### 文档结构

```
tech-notes/
├── docs/                    # 完整文档目录（主内容）
│   ├── README.md           # 📍 完整首页（主文档）
│   ├── EmbeddedSoft/       # 嵌入式软件模块
│   ├── MachineLearning/    # 机器学习模块
│   ├── Control_Vision/     # 电控与视觉模块
│   └── Projects/          # 项目实战
├── assets/                 # 静态资源
├── .github/               # GitHub 工作流
└── README.md              # 当前文件（导航页）
```

### 📝 如何贡献

欢迎对嵌入式系统、机器学习、控制算法等领域感兴趣的开发者一起完善这个知识库！

#### 贡献流程

1. **Fork 仓库**

   ```bash
   # 点击 GitHub 右上角 Fork 按钮
   # 克隆你的 fork
   git clone https://github.com/你的用户名/tech-notes.git
   ```

2. **创建分支**

   ```bash
   git checkout -b feature/主题名称
   # 例如：feature/add-rtos-tutorial
   ```

3. **添加或修改内容**

   - 技术笔记：在 `docs/` 对应目录下添加 `.md` 文件
   - 代码示例：在 `examples/` 目录添加代码文件
   - 修复错误：直接修改有问题的地方

4. **提交更改**

   ```bash
   git add .
   git commit -m "类型: 描述性信息"
   # 类型可选: docs, feat, fix, style, refactor
   # 例如: docs: 新增FreeRTOS任务调度详解
   ```

5. **发起 Pull Request**

   - 同步主仓库最新变更
   - 推送到你的分支
   - 在 GitHub 创建 Pull Request

#### 贡献指南

- **文档规范**

  - 使用中文为主，技术术语保留英文
  - 文件路径使用英文，避免空格和特殊字符
  - 图片资源存放在 `assets/images/` 对应子目录
  - 代码块标注语言类型（如 ```c, ```python）

- **内容要求**

  - 确保技术准确性，有官方文档或实验验证
  - 复杂的理论需配图说明
  - 代码示例应有注释和使用说明
  - 如果是翻译内容，注明原文出处

- **提交信息规范**

  ```
  类型(模块): 简短描述
  
  详细说明（可选）：
  - 修改的内容
  - 解决的问题
  - 相关issue编号
  
  类型说明：
  - docs: 文档更新
  - feat: 新功能/内容
  - fix: 错误修复
  - style: 格式调整
  - refactor: 重构内容
  ```

#### 🏆 贡献者名单

感谢所有为这个项目做出贡献的开发者！

[![贡献者](https://img.shields.io/github/contributors/CodeMzt/my-notes-site?style=for-the-badge)](https://github.com/CodeMzt/my-notes-site/graphs/contributors)

---

## 🔧 开发工具推荐

### 文档编写

- **VS Code** + Markdown All in One 插件
- **Typora** - 即时预览 Markdown 编辑器
- **Draw.io** - 技术图表绘制

### 嵌入式开发

- **STM32CubeIDE** - ARM 开发环境
- **FreeRTOS Kernel** - 实时操作系统
- **Wireshark** - 协议分析

### 机器学习

- **Jupyter Notebook** - 交互式实验
- **PyTorch/TensorFlow** - 深度学习框架
- **MLflow** - 实验跟踪

---

## 📄 许可证

本项目文档采用 [CC BY-NC-SA 4.0](LICENSE) 许可证，代码示例采用 MIT 许可证。

---

## 📮 联系与反馈

- **问题反馈**: [GitHub Issues](https://github.com/Mzt2006/tech-notes/issues)
- **技术讨论**: 欢迎在 Issues 中发起讨论
- **内容建议**: 直接提交 Pull Request 或 Issue

---

> ⭐ **如果这个项目对你有帮助，请给个 Star！**  

---

持续更新中...*
