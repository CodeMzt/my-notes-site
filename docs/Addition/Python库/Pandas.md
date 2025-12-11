# Pandas
	
Pandas 是在 NumPy 基础上构建的，专为**数据处理和分析**而设计的高效库。它是数据科学领域最核心的工具之一。
## Pandas 核心数据结构

Pandas 的核心是两个主要数据结构：**Series (系列)** 和 **DataFrame (数据框)**。

### 1. Series (系列)

**Series** 是一种一维的、带**标签（Label）** 的数组。你可以将其视为带索引的 NumPy 数组或带标签的单列数据表。

- **数据类型：** 可以容纳任何数据类型（整数、字符串、浮点数、Python 对象等）。
    
- **核心特性：**
    
    - **值 (Values)：** 底层是 NumPy 的 `ndarray`，保证了计算效率。
        
    - **索引 (Index)：** 赋予每个数据点一个明确的标签，用于更灵活地访问数据。
        

|**创建方式**|**示例**|
|---|---|
|从列表|`s = pd.Series([1, 3, 5, np.nan, 6, 8])`|
|从字典|`s = pd.Series({'a': 10, 'b': 20, 'c': 30})`|

### 2. DataFrame (数据框)

**DataFrame** 是一种二维的、表格型的数据结构，你可以将其视为一个 Excel 表格或 SQL 数据库中的表。它是 Pandas 最常用的对象。

- **核心结构：**
    
    - **行索引 (Index)：** 用于标记行（与 Series 共享）。
        
    - **列索引 (Columns)：** 用于标记列，每一列都是一个 **Series** 对象。
        
- **异构性：** 每一列可以有不同的数据类型，但**同一列**内的数据必须是同构的（所有元素类型相同）。
    

|**创建方式**|**示例**|
|---|---|
|从字典（最常用）|`data = {'col1': [1, 2], 'col2': [3, 4]}`<br><br>  <br><br>`df = pd.DataFrame(data)`|
|从 NumPy 数组|`dates = pd.date_range('20230101', periods=6)`<br><br>  <br><br>`df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))`|

---

## 数据查看与基本操作

### 3. 数据预览与信息

|**方法**|**描述**|
|---|---|
|**`df.head(n)`**|查看 DataFrame 的**前 n 行**（默认前 5 行）。|
|**`df.tail(n)`**|查看 DataFrame 的**后 n 行**（默认后 5 行）。|
|**`df.index`**|查看行索引。|
|**`df.columns`**|查看列名。|
|**`df.values`**|返回底层数据的 **NumPy 数组**表示。|
|**`df.dtypes`**|查看每列的数据类型。|
|**`df.info()`**|打印 DataFrame 的**简洁摘要**（包括内存使用、非空值数量）。|
|**`df.describe()`**|对数值列计算**描述性统计**（计数、均值、标准差等）。|

### 4. 数据选择 (Selection)

Pandas 提供了多种灵活的方式来选择数据。

- **列选择：** 像字典一样使用列名。
    
    - **单个 Series：** `df['col1']`
        
    - **多个 Series：** `df[['col1', 'col2']]`
        
- **按标签选择 (`loc`)：** 完全基于**行和列的标签**进行选择。
    
    - **单个值：** `df.loc[row_label, col_label]`
        
    - **切片：** `df.loc['2023-01-01':'2023-01-03', ['A', 'B']]`
        
- **按位置选择 (`iloc`)：** 完全基于**整数位置**进行选择（类似于 NumPy 索引）。
    
    - **单个值：** `df.iloc[row_position, col_position]`
        
    - **切片：** `df.iloc[0:3, 1:4]` （前 3 行，第 1 到 3 列）
        
- **布尔索引：** 使用布尔条件数组来过滤行。
    
    - **示例：** `df[df['A'] > 0]` 选出 A 列大于 0 的所有行。
        

---

## 数据处理与清洗

### 5. 缺失数据处理（Missing Data）

Pandas 默认使用 **`NaN` (Not a Number)** 来表示缺失值。

|**方法**|**描述**|
|---|---|
|**`df.dropna()`**|**删除**包含 `NaN` 的行或列。 `axis=0` (行，默认), `axis=1` (列)。|
|**`df.fillna(value)`**|用指定的值 **填充** `NaN`。例如：`df.fillna(0)`。|
|**`df.isnull()`**|返回一个布尔型 DataFrame，显示哪些位置是 `NaN`。|

### 6. 数据分组与聚合 (Group By)

`groupby()` 是 Pandas 中用于执行**分治-合并**（Split-Apply-Combine）策略的关键操作。

1. **分 (Split)：** 根据一个或多个键将数据分成组。
    
2. **应用 (Apply)：** 对每个组独立执行一个函数（如求和、均值、计数）。
    
3. **合并 (Combine)：** 将结果合并回一个数据结构。
    

- **基本操作：** `df.groupby('key_column').sum()`
    
- **多列分组：** `df.groupby(['key1', 'key2']).mean()`
    
- **多函数聚合：** 使用 **`agg()`** 方法。
    
    - **示例：** `df.groupby('key').A.agg(['mean', 'sum'])`
        

### 7. 数据合并与连接 (Merging & Joining)

用于将不同的 DataFrame **按键（Key）**或**索引（Index）**组合在一起。

| **方法**                             | **描述**                                                               | **SQL 对应** |
| ---------------------------------- | -------------------------------------------------------------------- | ---------- |
| **`pd.merge(df1, df2, on='key')`** | **按列值**连接 DataFrame，类似于 SQL 的 JOIN 操作。                               | `JOIN`     |
| **`pd.concat([df1, df2])`**        | **沿轴**堆叠或拼接 DataFrame 或 Series。 `axis=0` (垂直堆叠，默认), `axis=1` (水平堆叠)。 | `UNION`    |

### 8. 应用函数（Applying Functions）

- **`Series.apply(func)`：** 将函数应用于 Series 中的**每个元素**。
    
- **`DataFrame.apply(func)`：** 将函数应用于 DataFrame 的**每行或每列**。
    
    - `axis=0` 对**每列**应用函数。
        
    - `axis=1` 对**每行**应用函数。
        

---

## 笔记整理与常用速查表

|**分类**|**常用方法/参数**|**描述**|**关键点**|
|---|---|---|---|
|**数据结构**|`Series`, `DataFrame`|一维带标签数组，二维表格数据结构|**Series** 是 **DataFrame** 的列|
|**数据预览**|`head()`, `tail()`, `info()`, `describe()`|快速了解数据结构、缺失值和统计信息|`describe()` 仅用于数值列|
|**索引选择**|`df['col']`, `df.loc[]`, `df.iloc[]`|列选择、基于标签的选择、基于位置的选择|**`loc`** 用标签，**`iloc`** 用整数位置|
|**缺失值**|`fillna(0)`, `dropna(axis=0)`|填充或删除缺失值（`NaN`）||
|**分组聚合**|`groupby('col').agg(['mean', 'sum'])`|实现分治-合并的数据分析策略|使用 `agg()` 进行多函数聚合|
|**数据合并**|`pd.merge()`, `pd.concat()`|按键连接数据，或按轴堆叠数据|`merge()` 相当于 JOIN, `concat()` 相当于 UNION|
|**性能**|**向量化** 操作 (替代 Python 循环)|利用底层 NumPy 实现高速数据处理|尽量避免在 Pandas 中使用 `for` 循环|
