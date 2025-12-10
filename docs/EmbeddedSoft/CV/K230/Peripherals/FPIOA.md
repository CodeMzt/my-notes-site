参考：[FPIOA 使用教程 — CanMV K230](https://www.kendryte.com/k230_canmv/zh/main/zh/example/peripheral/fpioa.html)
# 概述

在嵌入式系统中，SoC（System on Chip）通常集成了多种外设模块，如 UART、SPI、I2C、PWM 和 GPIO 等。然而，由于物理引脚数量有限，这些模块往往需要**共享引脚**。为了解决这一冲突，就需要使用 **IOMUX（引脚复用）机制**。在 K230 芯片中，这一机制被称为 **FPIOA（Field Programmable IO Array）**。

> 在STM32中，这称为**AFIO**

FPIOA 允许我们为任意引脚分配所需的功能。例如，你可以将引脚 10 设置为 UART0 的发送脚，也可以设置为 GPIO 用于通用输入输出。

它充当了一个可配置的**交叉开关矩阵 (Crossbar Switch)**，允许将任意一个物理引脚映射到任意一个内部功能。

> **FPIOA 有什么作用？**
> 
> - **提升灵活性**：开发者可根据实际应用需求自由分配引脚功能。
>     
> - **减少限制**：一套硬件可适配多种引脚配置，便于模块化设计。

# `FPIOA` 模块 API 手册

## 概述

FPIOA（Pin Multiplexer）模块主要负责配置物理引脚（PAD）的功能。在 SoC 中，虽然有多种功能可用，但由于引脚数量有限，多个功能可能会共享同一个 I/O 引脚。此时，每个引脚在同一时刻只能激活一种功能，因此需要通过 IOMUX（即 FPIOA）来选择合适的功能。

## API 介绍

FPIOA 类位于 `machine` 模块中。

**示例**

```python
from machine import FPIOA

# 实例化 FPIOA 对象
fpioa = FPIOA()

# 打印所有引脚的配置
fpioa.help()

# 打印指定引脚的详细配置
fpioa.help(0)

# 打印指定功能的所有可用配置引脚
fpioa.help(FPIOA.IIC0_SDA, func=True)

# 设置 Pin0 为 GPIO0
fpioa.set_function(0, FPIOA.GPIO0)

# 设置 Pin2 为 GPIO2，同时配置其它参数
fpioa.set_function(2, FPIOA.GPIO2, ie=1, oe=1, pu=0, pd=0, st=1, ds=7)

# 获取指定功能当前所用的引脚
fpioa.get_pin_num(FPIOA.UART0_TXD)

# 获取指定引脚当前的功能
fpioa.get_pin_func(0)
```



### 实例化

```python
fpioa = FPIOA()
```



**参数**

无

### `set_function` 方法

```python
FPIOA.set_function(pin, func, ie=-1, oe=-1, pu=-1, pd=-1, st=-1, ds=-1)
```



设置引脚的功能。

**参数**(值为-1表示设置为默认参数)

- `pin`: 引脚号，范围：[0, 63]
- `func`: 功能号
- `ie`: 输入使能，可选参数
- `oe`: 输出使能，可选参数
- `pu`: 上拉使能，可选参数
- `pd`: 下拉使能，可选参数
- `st`: 施密特触发器使能，可选参数
- `ds`: 驱动能力，可选参数

**返回值**

无

| **参数** | **英文全称**    | **含义**             | **解释**                                                     |
| -------- | --------------- | -------------------- | ------------------------------------------------------------ |
| **`ie`** | Input Enable    | **输入使能**         | **`1`**：使能输入。引脚可以接收外部信号。用于将引脚配置为输入模式，无论是作为通用输入还是外设功能（如 UART RX, SPI MISO）。 |
| **`oe`** | Output Enable   | **输出使能**         | **`1`**：使能输出。引脚可以驱动外部负载。用于将引脚配置为输出模式，无论是作为通用输出还是外设功能（如 UART TX, SPI MOSI）。 |
| **`pu`** | Pull-Up         | **上拉电阻使能**     | **`1`**：使能内部上拉电阻。将引脚电压拉高到 VCC，常用于输入引脚，以确保在悬空时有确定的高电平。 |
| **`pd`** | Pull-Down       | **下拉电阻使能**     | **`1`**：使能内部下拉电阻。将引脚电压拉低到地 (GND)，常用于输入引脚，以确保在悬空时有确定的低电平。 |
| **`st`** | Schmitt Trigger | **施密特触发器使能** | **`1`**：使能施密特触发器。**用于输入引脚**。它引入回滞（Hysteresis），能有效消除输入信号的噪声和抖动，使不稳定信号转化为清晰的数字信号。 |
| **`ds`** | Drive Strength  | **驱动能力/强度**    | **取值范围通常是 1 到 8 或更高**。数字越大，引脚能提供的电流越大，信号的上升/下降速度越快，适用于高速通信。 |

### `get_pin_num` 方法

```python
fpioa.get_pin_num(func)
```



获取指定功能当前所在的引脚。

**参数**

- `func`: 功能号

**返回值**

返回引脚号，或 `None` 如果未找到相应功能。

### `get_pin_func` 方法

```python
fpioa.get_pin_func(pin)
```



获取指定引脚当前的功能。

**参数**

- `pin`: 引脚号

**返回值**

返回引脚当前的功能号。

### `help` 方法

```python
fpioa.help([number, func=False])
```



打印引脚配置提示信息。

**参数**

- `number`: 引脚号或功能号， 可选参数
- `func`: 是否启用功能号查询，默认为 `False`

**返回值**

可能为以下三种：

1. 所有引脚的配置信息（未设置 `number`）
2. 指定引脚的详细配置信息（设置了 `number`，未设置 `func` 或设置为 `False`）
3. 指定功能的所有可配置引脚号（设置了 `number`，并将 `func` 设置为 `True`）
