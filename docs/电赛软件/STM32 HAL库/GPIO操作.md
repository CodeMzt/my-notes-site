[TOC]
# **GPIO 基本概念与 CubeMX 配置流程**

**GPIO** (General Purpose Input/Output) 是微控制器与外部硬件进行交互的基础接口。在 STM32 中，每个 GPIO 引脚都可以独立配置为不同的模式和功能。
# GPIO结构
## 片上结构
![[../图源/GPIO基本结构.png]]
## 位结构
![[../图源/GPIO位结构.png]]
## **CubeMX 配置流程**

STM32CubeMX 是一个强大的图形化配置工具，用于生成初始化代码，极大地简化了 GPIO 的配置工作。

1. **引脚模式选择**：在芯片引脚图上，点击或右键点击要配置的引脚。
2. **模式配置**：选择所需的 GPIO 模式，例如：
   - **GPIO_Output**：通用推挽输出或开漏输出。
   - **GPIO_Input**：浮空输入、上拉输入或下拉输入。
   - **Alternate Function** (AF)：用于连接片上外设（如 USART、SPI、I2C 等）。
   - **Analog**：用于 ADC/DAC 等模拟功能。
3. **参数设置 (Parameters Settings)**：在左侧的 Pinout & Configuration 栏目中，选择 **GPIO** 选项卡。对每个启用的 GPIO 端口（如 PA, PB, PC...）进行详细配置：
   - **GPIO Mode**：确认引脚的输入/输出/复用功能。
   - **Pull-up/Pull-down**：设置上拉/下拉电阻（适用于输入模式）。
   - **Maximum Output Speed**：设置输出速度（Low, Medium, High, Very High）。
   - **User Label**：**强烈建议**为每个引脚设置一个清晰的别名（例如 `LED_R_Pin`, `KEY_WKUP_Pin`），这将直接反映在生成的 HAL 库代码中，提高代码可读性。

## **GPIO 工作模式**

GPIO 有四大工作模式，CubeMX 中配置的是这些模式的子集：

1. **输入模式 (Input Mode)**：用于从外部读取电平。可配置为**浮空**、**上拉**或**下拉**。
2. **输出模式 (Output Mode)**：用于向外部输出电平。可配置为**推挽**（能输出高低电平）或**开漏**（只能输出低电平或高阻态）。
3. **复用功能模式 (Alternate Function Mode)**：用于将引脚连接到芯片内部外设（如定时器、串口等）。
4. **模拟模式 (Analog Mode)**：用于 ADC/DAC 等模拟信号处理。

------

# **HAL 库 GPIO 核心 API**

HAL 库提供了一套简洁、统一的 API 来操作 GPIO，其函数命名通常遵循 `HAL_GPIO_...` 格式。

## **初始化**

- **`HAL_GPIO_Init(GPIO_TypeDef \*GPIOx, GPIO_InitTypeDef \*GPIO_Init)`**
  - **功能**：初始化指定的 GPIO 端口和引脚。
  - **使用方式**：这个函数由 CubeMX 根据你的配置自动生成，并在 `main.c` 中的 `MX_GPIO_Init()` 函数里被调用。**你无需手动调用或修改它，除非需要动态重新配置。**

## **输出操作（写操作）**

- **`HAL_GPIO_WritePin(GPIO_TypeDef \*GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState)`**

  - **功能**：设置指定引脚的输出电平。

  - **参数**：

    - `GPIOx`：GPIO 端口（如 `GPIOA`, `GPIOB` 等）。
    - `GPIO_Pin`：引脚号（使用 CubeMX 生成的别名，如 `LED_R_Pin`）。
    - `PinState`：电平状态（`GPIO_PIN_SET` 为高电平，`GPIO_PIN_RESET` 为低电平）。

  - **示例（点亮 LED）**：

    ```c
    HAL_GPIO_WritePin(GPIOB, LED_R_Pin, GPIO_PIN_RESET); // 假设低电平点亮
    ```

- **`HAL_GPIO_TogglePin(GPIO_TypeDef \*GPIOx, uint16_t GPIO_Pin)`**

  - **功能**：**翻转**指定引脚的输出电平。

  - **示例（LED 闪烁）**：

    ```c
    HAL_GPIO_TogglePin(GPIOB, LED_R_Pin);
    ```

## **输入操作（读操作）**

- **`GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef \*GPIOx, uint16_t GPIO_Pin)`**

  - **功能**：**读取**指定引脚的输入电平状态。

  - **返回值**：`GPIO_PinState` 类型（`GPIO_PIN_SET` 为高电平，`GPIO_PIN_RESET` 为低电平）。

  - **示例（读取按键状态）**：

    ```c
    if (HAL_GPIO_ReadPin(GPIOA, KEY_WKUP_Pin) == GPIO_PIN_RESET) {
        // 按键被按下（假设按键是下拉输入，按下时连接到 GND，读取低电平）
    }
    ```

------

# **外部中断（EXTI）与回调函数**


对于按键等需要实时响应的输入，通常配置为 **外部中断（EXTI）** 模式。

## EXTI基本结构
![[../图源/EXTI基本结构.png]]
## AFIO（复用IO口）说明

- AFIO主要用于引脚复用功能的选择和重定义

- 在STM32中，AFIO主要完成两个任务：复用功能引脚重映射、中断引脚选择
## EXTI框图
![[../图源/EXTI框图.png]]
## **EXTI 配置要点**

1. **引脚模式**：在 CubeMX 中将引脚配置为 **GPIO_EXTIxx**（例如 `GPIO_EXTI0`）。
2. **边沿检测**：配置中断触发的**边沿**（上升沿、下降沿或双边沿）。
3. **NVIC 使能**：在 **NVIC Settings** 中**使能**对应的 EXTI 中断线并设置优先级。

## **中断回调函数**

- **你需要实现的函数**：

  ```c
  void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
  {
      if (GPIO_Pin == KEY_WKUP_Pin) {
          // 在这里编写中断触发后的处理代码
          // 推荐：只设置标志位或发送消息，将耗时操作留给主循环
      }
  }
  ```

- **说明**：中断触发时，HAL 库会自动执行中断向量表中的 ISR（在 `stm32fxxx_it.c` 中），该 ISR 会调用一个通用的弱（`__weak`）回调函数。**你只需要在你的代码中重写（实现）这个 `HAL_GPIO_EXTI_Callback` 函数即可。**

### 说明

简而言之，`HAL_GPIO_EXTI_Callback` **对所有通过 GPIO 引脚触发的外部中断 (EXTI) 都有效**。

它是一个 **通用的、统一的回调函数**，用于处理所有连接到 EXTI 线的 GPIO 中断事件。

#### **HAL 库的抽象机制**

HAL 库通过一种多层嵌套的函数调用结构，将底层不同的中断向量抽象成一个统一的回调函数，这就是为什么你只需要实现一个 `HAL_GPIO_EXTI_Callback`：

1. 底层：硬件中断向量 (ISR)：

   你提到不同的外部中断有不同的中断向量，这是正确的。例如，STM32 F4 系列芯片中：

   - EXTI 线 0 对应一个向量（例如 `EXTI0_IRQHandler`）。

   - EXTI 线 1 对应一个向量（例如 `EXTI1_IRQHandler`）。

   - EXTI 线 10 到 15 共用一个向量（例如 EXTI15_10_IRQHandler）。

     这些函数位于 CubeMX 生成的 stm32fxx_it.c 文件中。

2. 中间层：HAL 库中断处理函数：

   在每个底层的中断服务程序 (ISR) 中，会调用 HAL 库提供的具体处理函数，例如：

   ```c
   // 位于 stm32fxx_it.c
   void EXTI0_IRQHandler(void)
   {
       HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); // 调用HAL库处理函数
   }
   ```

   HAL 库的这个处理函数会负责：

   - 清除对应的 **EXTI 挂起寄存器 (PR)** 标志。
   - 检查中断源是否真的被使能和触发。

3. 顶层：通用回调函数：

   HAL 库处理函数的最后一步，就是调用这个 弱（__weak） 声明的 HAL_GPIO_EXTI_Callback 函数，并将触发中断的引脚号作为参数传进去。

   - `__weak` 关键字允许你在你的应用代码（如 `main.c` 或驱动文件）中**重写**这个函数。
   - **参数 `GPIO_Pin`**：通过检查这个参数，你可以在一个回调函数中判断是哪个引脚触发了中断，从而执行不同的逻辑。

#### **如何区分不同的中断源？**

虽然回调函数是统一的，但你需要根据传入的 **`GPIO_Pin`** 参数来区分和处理不同的外部中断事件：

```c
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == KEY_START_Pin) {
        // 处理开始按键的逻辑
    } else if (GPIO_Pin == KEY_STOP_Pin) {
        // 处理停止按键的逻辑
    } else if (GPIO_Pin == RFID_DET_Pin) {
        // 处理 RFID 检测的逻辑
    }
    // 注意：无需手动清除挂起标志，HAL 库中间层已经处理了
}
```

## **注意事项**

- **消抖 (Debouncing)**：对于机械按键，务必在回调函数中或在后续处理中考虑软件消抖逻辑，防止引脚抖动导致多次误触发。

------

# **使用了 CubeMX 后**不用**关心什么？**

当你使用 STM32CubeMX 和 HAL 库进行开发时，CubeMX 已经为你处理了大量的底层配置和初始化工作。因此，作为应用开发者，你**几乎不用关心**以下这些细节：

| **细节类别**             | **描述**                                                     |
| ------------------------ | ------------------------------------------------------------ |
| **GPIO 时钟使能**        | **CubeMX 自动处理。** 在 `HAL_MspInit()` 函数中，CubeMX 已经自动生成了 `__HAL_RCC_GPIOx_CLK_ENABLE()` 调用，确保在使用端口前时钟已打开。 |
| **寄存器地址与位操作**   | **HAL 库封装了。** 你不需要直接操作 **MODER**、**OTYPER**、**PUPDR** 等寄存器来设置模式、类型或上下拉，只需使用 `HAL_GPIO_WritePin()` 等 API 即可。 |
| **底层初始化函数调用**   | **CubeMX 自动生成并调用。** `MX_GPIO_Init()` 函数会在 `main()` 函数中被调用。你无需关心它何时以及如何被调用。 |
| **NVIC 向量表配置**      | **CubeMX 自动配置。** 对于 EXTI，CubeMX 会自动配置并使能对应的 NVIC 中断通道，你只需要实现你的 **回调函数** 即可。 |
| **复位值 (Reset Value)** | **HAL 库负责初始化。** 启动时 GPIO 默认处于模拟或浮空状态，但 `HAL_GPIO_Init()` 会将其设置为你在 CubeMX 中配置的状态。你不用关心启动时的默认状态。 |

**总结：** CubeMX 的目标就是让你专注于使用 **HAL API**（如 `HAL_GPIO_WritePin`、`HAL_GPIO_ReadPin`）和实现 **回调函数**（如 `HAL_GPIO_EXTI_Callback`），而不用花费时间处理底层寄存器的配置细节。