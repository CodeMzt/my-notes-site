# Matplotlib

**Matplotlib** 是 Python 中最基础且最重要的数据可视化库。它提供了强大的、面向对象的 API，可以绘制出各种静态、动态或交互式的图表，是数据分析和科学研究中不可或缺的工具。
## Matplotlib 核心概念

Matplotlib 的核心是它的层次结构，理解这个结构是定制复杂图形的关键。

### 1. 层次结构：Figure, Axes, Axis

当你使用 Matplotlib 绘图时，你是在构建一个包含不同组件的层次结构：

- **Figure (画布)：** 顶层容器，可以理解为**整个窗口或页面**。它包含了所有的子图 (Axes) 和标题、图例等。
    
- **Axes (子图/坐标系)：** 实际绘图区域，是数据点、线条、文本等元素绘制的地方。**一个 Figure 可以包含多个 Axes**，每个 Axes 都有独立的 X 轴和 Y 轴。
    
- **Axis (坐标轴)：** 负责处理刻度线 (Ticks)、刻度标签 (Tick Labels) 和轴标签 (Labels)。
    

### 2. 两种绘图接口

Matplotlib 主要有两种使用方式：

|**接口名称**|**描述**|**优势**|
|---|---|---|
|**Pyplot 接口 (`plt`)**|基于状态机的方式，**快速绘图**。使用 `matplotlib.pyplot` 模块，它会自动创建 Figure 和 Axes。|简单快速，适用于简单图形。|
|**面向对象 (OO) 接口**|显式创建 Figure 和 Axes 对象，然后调用 Axes 对象的方法进行绘图。|**精细控制**图形的每个元素，适用于复杂的多子图布局。|

> **学习建议：** 掌握 OO 接口是进行高级定制和创建复杂图形的最佳途径。

---

## Matplotlib 基础绘图与 OO 接口

### 3. 使用面向对象接口绘图

这是 Matplotlib 的标准实践，用于获得最大的控制权：

1. **创建 Figure 和 Axes：** 使用 `plt.subplots()` 函数。
    
    - `fig, ax = plt.subplots()`
        
    - `fig` 是 Figure 对象，`ax` 是 Axes 对象 (一个子图)。
        
    - 对于多子图：`fig, axs = plt.subplots(nrows, ncols)`，此时 `axs` 是一个 Axes 对象的 NumPy 数组。
        
2. **调用 Axes 方法绘图：** 调用 Axes 对象的绘图方法，而不是 `plt.` 函数。
    
    - `ax.plot(x, y)` 绘制折线图。
        
    - `ax.scatter(x, y)` 绘制散点图。
        

### 4. 常用基本图表

所有这些绘图方法都应通过 **Axes 对象 (`ax.`)** 调用：

|**图表类型**|**Axes 方法**|**描述**|
|---|---|---|
|**折线图**|`ax.plot(x, y)`|随时间变化或连续数据的趋势展示。|
|**散点图**|`ax.scatter(x, y)`|展示两个变量之间的关系或数据点的分布。|
|**柱状图**|`ax.bar(x, height)`|比较不同类别之间的数据。|
|**直方图**|`ax.hist(data, bins)`|展示单个数值变量的频率分布。|
|**箱线图**|`ax.boxplot(data)`|展示数据的五数概括（中位数、四分位数、异常值）。|

### 5. 样式定制 (Customization)

通过设置 Axes 对象的方法来美化和注释图表：

- **设置标签和标题：**
    
    - `ax.set_title('图表标题')`
        
    - `ax.set_xlabel('X 轴标签')`
        
    - `ax.set_ylabel('Y 轴标签')`
        
- **添加图例：** `ax.legend(['数据系列1', '数据系列2'])`
    
- **设置刻度范围：** `ax.set_xlim(min_val, max_val)`, `ax.set_ylim(min_val, max_val)`
    
- **添加网格线：** `ax.grid(True)`
    

---

## 复杂布局与进阶操作

### 6. 多子图 (Subplots)

使用 `plt.subplots()` 是创建多子图布局最简单且最推荐的方法。

- **创建 2 行 1 列：** `fig, (ax1, ax2) = plt.subplots(2, 1)`
    
    - `ax1` 和 `ax2` 是独立的 Axes 对象，可以分别在其上绘图。
        
- **共享轴：** 在创建子图时可以指定共享 X 或 Y 轴。
    
    - `plt.subplots(2, 1, sharex=True)`
        

### 7. 保存图形

使用 Figure 对象的方法将图形保存到文件：

- `fig.savefig('my_plot.png', dpi=300)`
    
    - `dpi` 参数控制图片的分辨率。
        
    - 支持多种格式：`.png`, `.jpg`, `.pdf`, `.svg` 等。
        

### 8. 颜色、标记与线型 (Colormaps, Markers, Linestyles)

Matplotlib 提供了丰富的参数来控制图形的视觉样式：

- **颜色 (Color)：** 可以在绘图方法中使用 `color` 参数指定颜色名称（如 `'r'` 代表红色, `'b'` 代表蓝色）或十六进制代码。
    
- **线型 (Linestyle)：** 使用 `linestyle` 或简写 `ls` 参数（如 `'-'` 实线, `'--'` 虚线）。
    
- **标记 (Marker)：** 使用 `marker` 参数指定数据点的形状（如 `'o'` 圆圈, `'^'` 三角形）。
    

> **示例：** `ax.plot(x, y, color='green', linestyle='--', marker='o')`

---

## 笔记整理与常用速查表

|**主题**|**常用函数/方法**|**描述**|**接口**|
|---|---|---|---|
|**核心结构**|`plt.figure()`, `plt.subplots()`|创建画布 Figure 和 Axes（子图/坐标系）|OO|
|**绘图基础**|`ax.plot()`, `ax.scatter()`, `ax.bar()`, `ax.hist()`|在 Axes 上绘制各种基本图表|OO|
|**标签定制**|`ax.set_title()`, `ax.set_xlabel()`, `ax.legend()`|添加标题、轴标签、图例|OO|
|**多图布局**|`plt.subplots(R, C)`|创建 R 行 C 列的多子图布局|OO|
|**图形保存**|`fig.savefig(filename, dpi)`|将 Figure 对象保存为图像文件|OO|
|**快捷绘图**|`plt.plot()`, `plt.show()`|快速生成和显示图形|Pyplot|
