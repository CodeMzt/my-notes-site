# 📚 Mzt2006 技术笔记仓库

**嵌入式系统与机器学习的完整学习路径记录**

---

## 🌐 在线访问

👉 **完整文档网站：** [首页](docs/README.md)

---

## 📖 内容概览

本仓库是我个人在 **嵌入式系统** 与 **机器学习** 领域的系统性学习记录，采用双轨学习法同步推进两个核心技术方向。

### 🎯 核心学习模块

| 模块             | 技术方向                | 核心技术栈                                  |
| ---------------- | ----------------------- | ------------------------------------------- |
| **💻 嵌入式软件** | ARM架构、RTOS、底层驱动 | ARM Cortex-M, FreeRTOS, STM32 HAL, 通信协议 |
| **🤖 机器学习**   | 深度学习、计算机视觉    | PyTorch, TensorFlow, CNN/RNN, 模型部署      |
| **💡 电控与视觉** | 控制算法、嵌入式视觉    | PID/LQR/SMC, OpenCV, 机器人控制             |

### 🚀 快速导航

- **[嵌入式软件学习路径](docs/EmbeddedSoft/)** - 从ARM汇编到RTOS源码分析
- **[机器学习笔记](docs/MachineLearning/)** - PyTorch框架与深度学习实践
- **[电控与视觉算法](docs/Control_Vision/)** - 控制理论与计算机视觉应用
- **[项目实战案例](docs/Projects/)** - 综合应用实践项目

---

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

[![贡献者](https://img.shields.io/github/contributors/Mzt2006/tech-notes?style=for-the-badge)](https://github.com/Mzt2006/tech-notes/graphs/contributors)

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
> 📚 **完整文档请访问：[首页](docs/README.md)**

---

持续更新中...*