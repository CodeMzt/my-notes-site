# Seaborn

**Seaborn** 是一个基于 **Matplotlib** 的 Python 可视化库。它的目标是提供一个**高级接口**，用于绘制有吸引力且信息丰富的**统计图形**。

> **核心理念：** Seaborn 的设计高度集成 Pandas DataFrame，使得处理和可视化数据框变得非常高效和简单。相比于 Matplotlib 的底层控制，Seaborn 更侧重于数据本身的统计关系。

---
## Seaborn 核心概念与优势

### 1. 优势与定位

- **高级抽象：** 极大地简化了绘制复杂统计图表所需的代码。你无需处理大量的 Matplotlib 底层配置。
    
- **内置主题：** 提供美观且专业的默认图形样式和配色方案。
    
- **统计图类型：** 专注于可视化**单变量、双变量和多变量**的分布、关系和比较。
    
- **DataFrame 集成：** 大部分 Seaborn 函数可以直接接受 Pandas DataFrame 作为输入，使用列名来指定数据。
    

### 2. 核心函数类别

Seaborn 的函数可以大致分为以下几类，对应不同的统计目标：

|**类别**|**目标**|**常用函数示例**|
|---|---|---|
|**关系图 (Relational)**|可视化变量之间的关系（散点图、线图）|`relplot()`, `scatterplot()`, `lineplot()`|
|**分布图 (Distributional)**|可视化单变量或双变量的概率分布|`displot()`, `histplot()`, `kdeplot()`|
|**分类图 (Categorical)**|可视化分类变量与数值变量的关系（柱状图、箱线图）|`catplot()`, `boxplot()`, `violinplot()`, `barplot()`|
|**回归图 (Regression)**|可视化线性关系，并拟合回归线|`lmplot()`, `regplot()`|
|**矩阵图 (Matrix)**|可视化矩阵数据或层次聚类（热力图）|`heatmap()`|

---

## Seaborn 基础绘图与数据关系

### 3. 关系图 (Relational Plots)

这些图用于显示数据集中的观测值之间的统计关系。

- **`scatterplot()` (散点图)：** 最基本的关系图，用于显示两个数值变量之间的关系。
    
    - **关键参数：** `x`, `y` (数据列), `data` (DataFrame), `hue` (用于第三个分类变量着色)。
        
    - _示例：_ `sns.scatterplot(x="total_bill", y="tip", hue="time", data=df)`
        
- **`lineplot()` (线图)：** 用于显示随时间或序列变化的趋势，通常自动计算均值和置信区间。
    
    - _示例：_ `sns.lineplot(x="day", y="tip", data=df)`
        
- **`relplot()` (通用关系图)：** 结合散点图和线图，并允许使用 `col` 和 `row` 参数创建**多图网格** (Faceting)。
    

### 4. 分布图 (Distribution Plots)

这些图用于显示一个或多个变量的分布情况。

- **`histplot()` (直方图)：** 显示数值变量的频率分布。
    
    - _示例：_ `sns.histplot(data=df, x="total_bill", bins=15)`
        
- **`kdeplot()` (核密度估计图)：** 通过平滑的曲线估计概率密度函数，用于可视化变量的分布形状。
    
    - _示例：_ `sns.kdeplot(data=df, x="total_bill")`
        
- **`displot()` (通用分布图)：** 可以统一创建直方图 (`kind='hist'`)、核密度估计图 (`kind='kde'`) 或经验累积分布函数图 (`kind='ecdf'`)，并支持多图网格。
    

---

## Seaborn 分类与统计图

### 5. 分类图 (Categorical Plots)

用于比较分类变量与数值变量之间的关系。

- **`boxplot()` (箱线图)：** 显示数据分布的五数概括（中位数、四分位数、异常值）。
    
    - _示例：_ `sns.boxplot(x="day", y="total_bill", data=df)`
        
- **`violinplot()` (小提琴图)：** 结合了箱线图和核密度估计，显示数据分布的完整形状。
    
    - _示例：_ `sns.violinplot(x="day", y="total_bill", data=df)`
        
- **`barplot()` (条形图)：** 显示每个分类 bin 的**均值**和**置信区间**（默认）。
    
    - _示例：_ `sns.barplot(x="day", y="total_bill", data=df)`
        
- **`catplot()` (通用分类图)：** 统一的接口，用于绘制所有分类图（如箱线图、小提琴图、条形图等），并支持多图网格。
    

### 6. 矩阵图 (Matrix Plots)

用于可视化矩阵数据。

- **`heatmap()` (热力图)：** 将数据矩阵的值映射到颜色。常用于可视化**相关系数矩阵**或**混淆矩阵**。
    
    - **关键参数：** `data` (二维数组或 DataFrame), `annot=True` (在单元格内显示数值)。
        
    - _示例：_ `sns.heatmap(df.corr(), annot=True, cmap='coolwarm')`
        

---

## 样式与高级控制

### 7. 主题与样式设置

Seaborn 允许你使用内置的主题和样式函数来美化图形：

- **设置主题：** `sns.set_theme()` 或 `sns.set_style(style)`
    
    - `style` 选项包括：`'darkgrid'`, `'whitegrid'`, `'dark'`, `'white'`, `'ticks'`.
        
- **设置调色板：** `sns.set_palette(palette)`
    
    - 可以设置 Matplotlib 调色板名称或 Seaborn 自己的调色板。
        

### 8. Matplotlib 结合

由于 Seaborn 是建立在 Matplotlib 上的，因此你可以使用 Matplotlib 的 OO 接口对 Seaborn 生成的图形进行**精细定制**。

1. **获取 Axes 对象：** 大多数 Seaborn 函数都会返回 Matplotlib 的 Axes 对象。
    
2. **定制：** 使用 `ax.set_title()`, `ax.set_xlabel()`, `plt.tight_layout()` 等 Matplotlib 函数进行修改。
    

---

## 笔记整理与常用速查表

|**主题类别**|**目标**|**常用 Seaborn 函数**|**关键参数**|**Matplotlib 对应**|
|---|---|---|---|---|
|**关系**|变量间趋势|`scatterplot()`, `lineplot()`|`x`, `y`, `hue`, `data`|`ax.scatter()`, `ax.plot()`|
|**分布**|变量频率/密度|`histplot()`, `kdeplot()`, `displot()`|`x`, `y`, `bins`, `kind`|`ax.hist()`|
|**分类**|类别比较|`boxplot()`, `barplot()`, `violinplot()`|`x` (分类), `y` (数值), `data`|无直接对应|
|**矩阵**|关联强度|`heatmap()`|`annot=True`, `cmap`|`ax.imshow()`|
|**通用**|多图网格|`relplot()`, `catplot()`, `displot()`|`col`, `row` (用于分面)|`plt.subplots()`|
|**样式**|主题美化|`sns.set_theme()`, `sns.set_style()`|`'darkgrid'`, `'whitegrid'`||
