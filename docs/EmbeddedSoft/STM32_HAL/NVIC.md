# 基本结构
![](../photosource/NVIC基本结构.png)

# **NVIC 核心概念与工作原理**

**NVIC (Nested Vectored Interrupt Controller)** 是 ARM Cortex-M 内核（STM32 采用）中一个高度集成的模块，专门负责管理系统中的所有中断。

## **1. 中断向量表 (Vector Table)**

- **定义**: 这是一个内存地址表格，存放了所有中断服务程序（ISR）的入口地址。
  
- **作用**: 当一个中断事件发生时，NVIC 会查询向量表，获取对应的 ISR 地址，并跳转执行。
  
- **STM32 特性**: 向量表通常位于 Flash 或 SRAM 的起始地址，其基地址是可编程的（通过 SCB 寄存器）。CubeMX 生成的项目中，向量表默认位于 Flash 的起始地址。
  

## **2. 中断源分类**

STM32 的中断源大致分为两类：

|**类型**|**描述**|**示例**|**优先级设定**|
|---|---|---|---|
|**内核异常 (Core Exceptions)**|由 CPU 内核内部产生，用于处理系统错误或调试。|Reset, NMI, Hard Fault, SysTick|拥有固定的优先级和**可编程的子优先级**|
|**外部中断 (External Interrupts)**|由片上外设（Peripherals）或外部引脚产生。|EXTI, USART, SPI, TIM, ADC|优先级完全**可编程**|

## **3. 优先级管理 (Priority Management)**

NVIC 的核心职能是处理多重中断的抢占和仲裁。

- **抢占优先级 (Preemption Priority)**：这是中断的首要决定因素。**高抢占优先级的中断可以打断（抢占）低抢占优先级的中断。**
  
- **子优先级 (Sub-Priority / Sub-Group Priority)**：当两个中断的**抢占优先级相同**时，子优先级才发挥作用。它决定了在相同抢占级别下，哪个中断先被服务（但不能互相抢占）。
  
- **优先级分组 (Priority Grouping)**：ARM Cortex-M 允许开发者将 8 位（或更少）的优先级字段分成抢占优先级和子优先级两部分。
  
    - 例如，如果配置为 **Group 2**（CubeMX 默认），则优先级字段的最高 4 位用于抢占优先级，最低 0 位用于子优先级（即没有子优先级）。
      
    - **CubeMX 默认分组**：STM32 HAL 库通常默认使用 **Group 4**（即 4 位用于抢占优先级，0 位用于子优先级），或 **Group 3**（3 位抢占，1 位子优先级），具体取决于芯片系列和 HAL 库版本。
      

> **优先级数值规则**：
> 
> - NVIC 中，**数值越小，优先级越高**（0 是最高优先级）。
>     
> - 抢占优先级高的中断才能抢占正在执行的低优先级中断。

| 分组方式 | 抢占优先级     | 响应优先级      |
| ---- | --------- | ---------- |
| 分组0  | 0位，取值为0   | 4位，取值为0~15 |
| 分组1  | 1位，取值为0~1 | 3位，取值为0~7  |
| 分组2  | 2位，取值为0~3 | 2位，取值为0~3  |
| 分组3  | 3位，取值为0~7 | 1位，取值为0~1  |
|分组4|4位，取值为0~15|0位，取值为0|
# STM32CubeMX 中的 NVIC 配置 

CubeMX 极大地简化了 NVIC 的配置工作，使其图形化、可视化。

## **1. 优先级分组配置**

- **路径**: Pinout & Configuration $\rightarrow$ **System Core** $\rightarrow$ **NVIC**。
  
- **配置项**: **Priority Group**。
  
    - **HAL 库默认值**: 常见为 `NVIC Priority Group 4` (或 `__NVIC_PRIO_BITS` 决定的分组)。
      
    - **意义**: Group 4 意味着所有可用优先级位（通常 4 位）都分配给**抢占优先级**，没有子优先级。这保证了优先级设定的直观性和抢占的确定性。
      
    - **建议**: 在项目开发中，**不要轻易修改** CubeMX 默认的优先级分组，除非你对中断抢占机制有非常深入的理解和特殊要求。
      

## **2. 外部中断配置**

- **路径**: Pinout & Configuration $\rightarrow$ **NVIC Settings** (在每个外设或 EXTI 的配置页面中)。
  
- **操作**:
  
    1. 找到目标外设（如 TIM3、USART1 或 EXTI Line 0）。
       
    2. 勾选对应的中断线（如 `TIM3 global interrupt`）。
       
    3. 设置 **Preemption Priority**（抢占优先级）和 **Subpriority**（子优先级）。
       

> **CubeMX 细节**：如果你选择了 Group 4（0 位子优先级），那么 Subpriority 字段将无法编辑，你只需关注 Preemption Priority。

---

# **HAL 库与 NVIC 相关的 API 

HAL 库提供了一套简洁的 API 来管理 NVIC。这些函数通常由 CubeMX 自动生成，但你也可以在运行时动态调用它们。

## **1. 优先级分组配置 (自动)**

- **函数**: `HAL_NVIC_SetPriorityGrouping(uint32_t PriorityGroup)`
  
- **说明**: 此函数设置优先级分组。CubeMX 会在 `HAL_Init()` 或 `MX_NVIC_Init()` 中自动调用它，使用你在配置界面选择的分组（通常是 `NVIC_PRIORITYGROUP_4`）。
  

## **2. 配置和设置优先级 (自动/手动)**

- **函数**: `HAL_NVIC_SetPriority(IRQn_Type IRQn, uint32_t PreemptPriority, uint32_t SubPriority)`
  
- **说明**: 用于设置特定中断源的抢占优先级和子优先级。
  
    - `IRQn`: 中断请求号（例如 `TIM3_IRQn`, `USART1_IRQn`）。
      
    - CubeMX 会在 `MX_NVIC_Init()` 中为所有启用的中断源自动生成调用。
    
    ```c
    // 示例：CubeMX 自动生成的代码片段
    HAL_NVIC_SetPriority(TIM3_IRQn, 0, 0); // 设置 TIM3 中断，抢占优先级为 0
    HAL_NVIC_EnableIRQ(TIM3_IRQn);
    ```
    

## **3. 中断的使能与禁用**

- **函数**: `HAL_NVIC_EnableIRQ(IRQn_Type IRQn)`
  
- **函数**: `HAL_NVIC_DisableIRQ(IRQn_Type IRQn)`
  
- **说明**: 用于在运行时动态开启或关闭特定的中断请求。
  
    - **注意**: 即使在 CubeMX 中启用了中断，在进入 `main()` 函数之前，这些中断通常仍处于禁用状态。`MX_NVIC_Init()` 会在初始化阶段调用 `HAL_NVIC_EnableIRQ` 宏来使能它们。
      

## **4. 中断挂起与清除**

- **函数**: `HAL_NVIC_SetPendingIRQ(IRQn_Type IRQn)`
  
- **函数**: `HAL_NVIC_ClearPendingIRQ(IRQn_Type IRQn)`
  
- **说明**: 用于软件模拟中断触发（设置挂起标志）或清除挂起标志。一般不常用，但在测试和特殊同步机制中可能用到。
  

---

# **中断服务程序 (ISR) 与回调函数机制**

理解 HAL 库如何处理 ISR 是使用中断的关键。

## **1. 中断向量表与 ISR (由 CubeMX 生成)**

- **文件**: `stm32fxxx_it.c`
  
- **内容**: 这个文件包含了所有**中断向量表**指向的入口函数，例如 `TIM3_IRQHandler`。
  
- **HAL 库的作用**: 这些 ISR 函数内部通常只做两件事：
  
    1. 调用 HAL 库提供的通用处理函数（例如 `HAL_TIM_IRQHandler(&htim3)`）。
       
    2. 在这个通用处理函数内部，HAL 库会清除中断标志位，并最终调用**回调函数**。
       

## **2. 中断回调函数 (你需要实现)**

- **机制**: HAL 库将底层的 ISR 抽象成用户友好的 **弱（`__weak`）回调函数**。
  
- **示例**:
  
    - **定时器溢出**：你需要实现 `HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)`
      
    - **GPIO 外部中断**：你需要实现 `HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)`。
    
- **你的任务**: 你只需要在你的应用代码（如 `main.c` 或你的驱动文件）中**重写**这些回调函数，实现你的业务逻辑。
  

> **核心原则**: HAL 库帮你处理了所有寄存器级别的操作（清除标志位、跳转），你只需要专注于实现回调函数中的业务逻辑即可。