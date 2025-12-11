# Numpy库
## NumPy 核心概念与基础操作

### 1. `ndarray`：NumPy 的核心对象

NumPy 的核心是其 **`ndarray`** 对象（N 维数组），它是一个存储同类型数据的多维容器。

- **同构性：** 数组中的所有元素必须是**相同的数据类型**（dtype）。
    
- **效率：** 它的设计极大地优化了内存使用和计算速度，特别是在进行大规模数据操作时，比 Python 原生的列表快得多。
    

### 2. 创建数组（Creation）

创建 `ndarray` 是第一步，有多种常用的方法：

|**方法**|**描述**|**示例**|
|---|---|---|
|**从 Python 列表/元组**|使用 `np.array()`|`np.array([1, 2, 3])`|
|**全零数组**|使用 `np.zeros(shape)`|`np.zeros((2, 3))`|
|**全一数组**|使用 `np.ones(shape)`|`np.ones((1, 5))`|
|**等差数列**|使用 `np.arange(start, stop, step)`|`np.arange(0, 10, 2)`|
|**均匀分布的数值**|使用 `np.linspace(start, stop, num)`|`np.linspace(0, 1, 5)`|
|**单位矩阵/对角线为 1**|使用 `np.eye(N)`|`np.eye(3)`|

### 3. 数组属性（Attributes）

理解数组的结构至关重要，以下是几个关键属性：

- **`ndim`：** 数组的**维数**（轴的数量）。
    
- **`shape`：** 数组在每个维度上的**大小**（元组形式）。
    
- **`size`：** 数组中**元素的总数**。
    
- **`dtype`：** 数组元素的**数据类型**（如 `int64`, `float32`）。
    

### 4. 索引与切片（Indexing & Slicing）

NumPy 的索引和切片类似于 Python 列表，但扩展到了多维：

- **基本索引：** 访问单个元素，使用逗号分隔每个维度索引。
    
    - **一维：** `arr[i]`
        
    - **二维：** `arr[row, col]`
        
- **切片：** 提取子数组，使用冒号 `:`。
    
    - **示例：** `arr[0:2, 1:]` 提取第 0 到 1 行（不包含 2）和第 1 列及之后的所有列。
        
- **布尔索引（Fancy Indexing）：** 使用布尔数组来选择元素。
    
    - **示例：** `arr[arr > 5]` 返回所有大于 5 的元素组成的新数组。
        

---

## NumPy 数组操作与函数

### 5. 形状操作（Reshaping）

改变数组的维度而不改变其数据：

- **`reshape()`：** 将数组转换为指定的新形状。新形状的**元素总数必须与原数组相同**。
    
    - **特殊用法：** 使用 `-1` 作为形状参数时，NumPy 会自动计算该维度的大小。
        
    - **示例：** `arr.reshape(2, 5)`
        
- **`ravel()` / `flatten()`：** 将数组展平为一维数组。
    
    - `ravel()` 返回视图（可能），`flatten()` 返回副本。
        
- **转置：** `arr.T` 或 `np.transpose(arr)`
    

### 6. 算术运算（Arithmetic Operations）

NumPy 的强大之处在于其**向量化**操作，即数组间的操作是元素级的，无需显式的 Python 循环。

- **元素级运算：** * 加、减、乘、除：`+`, `-`, `*`, `/`
    
    - **注意：** 两个数组相乘 `A * B` 是元素级乘法 (Hadamard 积)，**不是矩阵乘法**。
        
- **矩阵乘法：** 使用 `np.dot(A, B)` 或 `@` 运算符 (Python 3.5+)
    
    - **示例：** `A @ B`
        

### 7. 通用函数（Universal Functions, ufuncs）

**ufuncs** 是对 `ndarray` 执行元素级操作的函数，例如：

- **数学函数：** `np.sqrt()`, `np.exp()`, `np.log()`, `np.sin()`
    
- **比较函数：** `np.maximum()`, `np.minimum()`
    

### 8. 聚合函数（Aggregation Functions）

这些函数用于从数组中计算单个统计量：

- **求和：** `np.sum(arr)` 或 `arr.sum()`
    
- **均值：** `np.mean(arr)`
    
- **标准差：** `np.std(arr)`
    
- **最大/小值：** `np.max(arr)`, `np.min(arr)`
    
- **最大/小值索引：** `np.argmax(arr)`, `np.argmin(arr)`
    

> **轴（Axis）的概念：** 在聚合函数中，可以通过 **`axis`** 参数指定计算沿着哪个轴进行。
> 
> - `axis=0` 表示沿着**行**（垂直方向）操作，压缩行，返回列的统计量。
>     
> - `axis=1` 表示沿着**列**（水平方向）操作，压缩列，返回行的统计量。
>     

---

## 笔记整理与常用速查表

|**主题**|**常用函数/方法**|**描述**|**关键属性**|
|---|---|---|---|
|**数组创建**|`np.array()`, `np.zeros()`, `np.ones()`, `np.arange()`, `np.linspace()`|初始化 `ndarray`|`dtype`, `shape`, `ndim`, `size`|
|**数组索引**|`arr[i, j]`, `arr[:, j]`, `arr[arr > 5]`|访问和提取子数组||
|**形状操作**|`arr.reshape()`, `arr.T`, `arr.ravel()`|改变数组的维度和排列||
|**算术运算**|`A + B`, `A * B`, `A @ B` 或 `np.dot(A, B)`|元素级运算和矩阵乘法||
|**聚合统计**|`np.sum()`, `np.mean()`, `np.std()`, `np.max()`, `np.argmax()`|计算统计指标|`axis` 参数控制方向|
|**连接/拆分**|`np.concatenate()`, `np.vstack()`, `np.hstack()`, `np.split()`|组合或拆分多个数组||
|**通用函数**|`np.sqrt()`, `np.exp()`, `np.log()`|元素级的数学操作||
