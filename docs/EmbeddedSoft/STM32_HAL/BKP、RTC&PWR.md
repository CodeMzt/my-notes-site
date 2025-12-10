# BKP、RTC&PWR
# **1. RTC (Real-Time Clock) 实时时钟**

## **RTC 结构与工作原理**

RTC 模块是 STM32 芯片中一个独立且高度专业的计数器，其设计核心是围绕**低功耗**和**掉电保持**。

### **核心结构组成**



1. **时钟源 (RTC Clock Source)**：
   - 通常选择 **LSE (Low Speed External)** 32.768 kHz 晶振，因为它具有高精度和低功耗特性。
   - 也可以选择 LSI（内部低速 RC 振荡器）或 HSE/128（通常为8MHz/128）。
2. **计数器**
   - 32位的可编程计数器，可对应Unix时间戳的秒计数器。（1s增加1次，理论上很久很久才会溢出）
3. **预分频器 (RTC Prescalers)**：
   - 包含 **异步预分频器 (Asynchronous Prescaler)** 和 **同步预分频器 (Synchronous Prescaler)**。
   - 20位的可编程预分频器。
   - 它们的任务是将 32.768 kHz 输入时钟精确分频，最终得到 **1 Hz 的时基**（每秒产生一次脉冲）。
   - $$f_{\text{out}} = \frac{f_{\text{in}}}{(\text{Asynch} + 1) \times (\text{Synch} + 1)} = 1 \text{ Hz}$$
4. **时间/日历寄存器**：
   - 直接存储秒、分、时、日、月、年、星期等 BCD (Binary Coded Decimal) 格式的数据。
5. **报警/唤醒逻辑**：
   - 包含报警寄存器（Alarm A/B）和唤醒定时器，用于在特定时间或周期性地产生事件。

## **CubeMX RTC 配置与实现**

| **概念**     | **描述**                                                     |
| ------------ | ------------------------------------------------------------ |
| **独立电源** | RTC 模块由专用的 **VBAT** 引脚供电（通常是纽扣电池）。即使主电源 $V_{DD}$ 断电，RTC 也能保持运行和计时。 |
| **时钟源**   | RTC 可以选择多种时钟源，最常用的是 **LSE (Low Speed External)**，即 32.768 kHz 外部晶振，精度最高。 |
| **日历功能** | RTC 模块内部可以存储秒、分、时、日、月、年、星期等信息，并支持闰年自动补偿。 |
| **报警功能** | 可以设置两个独立的报警时间（Alarm A 和 Alarm B），当时间匹配时产生中断。 |
| **唤醒功能** | 周期性地唤醒系统或产生中断。                                 |

配置 RTC 往往是配置整个备份域的第一步。

### **1. 时钟源配置 (RCC)**

1. **Pinout & Configuration $\rightarrow$ System Core $\rightarrow$ RCC**。
2. 在 **LSE** 选项中，选择 `Crystal/Ceramic Resonator` (使用外部 32.768 kHz 晶振)。

### **2. RTC 模式配置**

1. **Pinout & Configuration $\rightarrow$ Timers $\rightarrow$ RTC**。
2. **Activate Clock Source**：**必须勾选**。
3. **Parameter Settings (关键)**：
   - **Asynchronous Predivider** 和 **Synchronous Predivider**：这两个预分频器将 32.768 kHz 时钟源分频，最终得到 **1 Hz**（1秒钟计数一次）。
     - **公式**: $\text{LSE} / ((\text{Asynch} + 1) \times (\text{Synch} + 1)) = 1 \text{ Hz}$
     - CubeMX 会自动计算，确保结果为 1 Hz。
   - **Hour Format**：选择 12 小时制 (`12 Hour Format`) 或 24 小时制 (`24 Hour Format`)。

### **3. NVIC 配置（如果需要中断）**

1. 在 RTC 配置页面的 **NVIC Settings** 中。
2. 勾选 `RTC global interrupt`（RTC 报警或唤醒中断）。
3. 设置优先级。

### **HAL 库 RTC 核心 API 与实现**

#### **1. RTC 初始化与设置时间**

在 `main()` 函数中，通常在 `MX_RTC_Init()` 之后调用以下函数来设置初始时间和日期。

```c
// 定义时间结构体和日期结构体
RTC_TimeTypeDef sTime = {0};
RTC_DateTypeDef sDate = {0};

// 设置时间（例如 14:30:00）
sTime.Hours = 14;
sTime.Minutes = 30;
sTime.Seconds = 0;
// sTime.DayLightSaving = RTC_DAYLIGHTSAVING_NONE; // 夏令时，通常不用
// sTime.StoreOperation = RTC_STOREOPERATION_RESET;

// 设置日期（例如 2025年12月7日，星期日）
sDate.WeekDay = RTC_WEEKDAY_SUNDAY;
sDate.Month = RTC_MONTH_DECEMBER;
sDate.Date = 7;
sDate.Year = 25; // HAL 库中只用后两位

// 将时间信息写入 RTC
HAL_RTC_SetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
HAL_RTC_SetDate(&hrtc, &sDate, RTC_FORMAT_BIN);
```

#### **2. 读取时间和日期**

读取时必须**先读取时间，再读取日期**，因为 RTC 在读取时间时会锁存日期寄存器，防止读数过程中的更新。

```c
// 临时变量用于存储读出的结果
RTC_TimeTypeDef gTime = {0};
RTC_DateTypeDef gDate = {0};

// 先读取时间（会锁存日期）
if (HAL_RTC_GetTime(&hrtc, &gTime, RTC_FORMAT_BIN) == HAL_OK) {
    // 后读取日期
    HAL_RTC_GetDate(&hrtc, &gDate, RTC_FORMAT_BIN);
    
    // 打印或使用 gTime 和 gDate
    printf("Current Time: %02d:%02d:%02d\n", gTime.Hours, gTime.Minutes, gTime.Seconds);
}
```

#### **3. 报警功能设置 (中断)**

使用 `HAL_RTC_SetAlarm_IT` 设置报警时间并启用中断。

```c
RTC_AlarmTypeDef sAlarm = {0};

// 假设我们设置 Alarm A 在每天的 15:00:00 报警
sAlarm.AlarmTime.Hours = 15;
sAlarm.AlarmTime.Minutes = 0;
sAlarm.AlarmTime.Seconds = 0;

// 配置报警匹配方式：只匹配时/分/秒，日期和星期不匹配
sAlarm.AlarmMask = RTC_ALARMMASK_DATEWEEKDAY; 
sAlarm.Alarm = RTC_ALARM_A;

// 设置报警并启动中断
HAL_RTC_SetAlarm_IT(&hrtc, &sAlarm, RTC_FORMAT_BIN);
```

#### **4. 报警中断回调函数**

```c
void HAL_RTC_AlarmAEventCallback(RTC_HandleTypeDef *hrtc)
{
    // 报警 A 事件发生，执行任务
    printf("Alarm A Triggered!\n");
}
```

------

# **2. BKP (Backup Registers) 备份寄存器**

## **BKP 结构与访问**

BKP 寄存器是位于 **RTC 域** 的一组 SRAM 单元，用于存储用户数据，其最大的特点是**独立于主电源供电**。

## **BKP 核心特性**

- **非易失性存储**：BKP 寄存器同样由 **VBAT** 供电，因此即使主电源断电，存储在其中的数据也不会丢失。
- **容量**：不同系列的 STM32 芯片容量不同，例如 F1 系列有 42 个 16 位寄存器，而 F4/F7/H7 系列有数百个 32 位寄存器（称为 RTC-BKP 寄存器）。
- **用途**：存储系统状态、校准参数、上电计数器、或用于判断系统是**正常重启**还是**首次上电**。

### **核心结构组成**

1. **供电**：与 RTC 共享 **VBAT** 电源。
2. **存储单元**：由一系列 **32 位**（或老系列中的 16 位）通用寄存器 (`RTC_BKP_DRx`) 组成。
3. **写保护**：由 **DBP (Disable Backup Protection)** 位控制。在任何写入 BKP 寄存器或 RTC 相关的配置时，必须先清除写保护。

## **访问 BKP 区域的特殊要求**

由于 BKP 区域与 RTC 共享电源和时钟，访问 BKP 寄存器需要特殊的步骤：

1. **使能时钟**：(设置RCC_APB1ENR的PWREN和BKPEN,)使能 **PWR（电源）** 和 **BKP（或 DBP）** 域的时钟。
2. **失能写入保护**：STM32 默认对备份域开启了**写保护**，必须禁用该保护才能写入数据。(设置PWR_CR的DBP)
3. 若在读取RTC寄存器时，RTC的APB1接口曾经处于禁止状态，则软件首先必须等待RTC_CRL寄存器中的RSF位（寄存器同步标志）被硬件置1
4. 必须设置RTC_CRL寄存器中的CNF位，使RTC进入配置模式后，才能写入RTC_PRL、RTC_CNT、RTC_ALR寄存器
5. 对RTC任何寄存器的写操作，都必须在前一次写操作结束后进行。可以通过查询RTC_CR寄存器中的RTOFF状态位，判断RTC寄存器是否处于更新中。仅当RTOFF状态位是1时，才可以写入RTC寄存器

## **HAL 库 BKP 核心 API 与实现**

### **1. 访问 BKP 区域的通用步骤 (HAL 库自动封装)**

在 HAL 库中，操作 RTC 和 BKP 寄存器时，通常需要以下步骤：

```c
// 1. 启动电源接口时钟
__HAL_RCC_PWR_CLK_ENABLE(); 
// 2. 使能对备份域的访问（禁用写保护）
HAL_PWR_EnableBkUpAccess(); 

// ... 执行 BKP 或 RTC 读写操作 ...

// 3. 禁用对备份域的访问（重新启用写保护，可选）
HAL_PWR_DisableBkUpAccess();
```

> **注意**: 在 CubeMX 生成的代码中，`HAL_PWR_EnableBkUpAccess()` 已经被封装在 `HAL_RTC_Init()` 的开头，所以通常不需要手动调用。

### **2. 写入 BKP 寄存器**

BKP 寄存器在 HAL 库中被抽象为 `RTC_BKP_DRx`（x 为寄存器编号）。

```c
// 假设我们要向 BKP 寄存器 DR1 写入一个魔数（Magic Number）
#define BKP_MAGIC_NUMBER 0xABCDABCD
#define BKP_INDEX RTC_BKP_DR1

// 确保备份域写保护已禁用（通过 HAL_PWR_EnableBkUpAccess()）

// 写入数据
HAL_RTCEx_BKUPWrite(&hrtc, BKP_INDEX, BKP_MAGIC_NUMBER);
```

### **3. 读取 BKP 寄存器**

读取操作不需要禁用写保护。

```c
uint32_t read_value;

// 读取 BKP 寄存器 DR1 的值
read_value = HAL_RTCEx_BKUPRead(&hrtc, BKP_INDEX);

if (read_value == BKP_MAGIC_NUMBER) {
    // BKP 数据有效，系统是正常重启
    printf("System rebooted normally.\n");
} else {
    // BKP 数据无效（例如第一次上电或 VBAT 断电），需要重新初始化
    printf("First power on or VBAT lost. Initializing BKP.\n");
}
```

### **4. 综合应用：判断首次上电**

这是 BKP 寄存器最经典的应用场景。

1. **初始化流程**:

   - 读取 BKP 寄存器（如 DR1）。
   - 如果读出的值不等于预设的魔数（即随机设定的数，例如 0x1234），说明这是**首次上电**或 **VBAT 断电**。
     - 此时，调用 `HAL_RTC_SetTime/SetDate` 设置初始时间。
     - 向 BKP 写入魔数 0x1234。
   - 如果读出的值等于魔数，说明 RTC 时间是有效的，**无需重新设置**。

2. **代码骨架**:

   ```c
   #define VALID_FLAG 0x1234
   
   // 在 main() 函数中，初始化 RTC 句柄后：
   if (HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR1) != VALID_FLAG)
   {
       // 第一次启动，设置RTC时间和BKP
       Set_Initial_RTC_Time(); 
       HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR1, VALID_FLAG);
   }
   // 否则，RTC会继续计时
   ```

------

# **3. PWR (Power Control) 电源控制模块详解**

**PWR** 模块是配置和控制整个芯片电源域（包括备份域）的关键。RTC 和 BKP 的所有操作都依赖于 PWR 模块的授权。

## **PWR 核心作用**

1. **备份域控制**：控制对 RTC 和 BKP 寄存器区域的**写访问保护**。
2. **低功耗模式**：PWR负责管理STM32内部的电源供电部分，可以实现可编程电压监测器和低功耗模式的功能。低功耗模式包括睡眠模式（Sleep）、停机模式（Stop）和待机模式（Standby），可在系统空闲时，降低STM32的功耗，延长设备使用时间
3. **电压监测**：管理 PVD (Programmable Voltage Detector) 功能。可编程电压监测器（PVD）可以监控VDD电源电压，当VDD下降到PVD阀值以下或上升到PVD阀值之上时，PVD会触发中断，用于执行紧急关闭任务

## **CubeMX PWR 配置细节**

1. **Pinout & Configuration $\rightarrow$ System Core $\rightarrow$ PWR**。
2. **Parameter Settings**:
   - **Voltage Regulator Output**: 通常设置为 `Reset`（默认操作）。
   - **PVD (Programmable Voltage Detector)**：可选配置，用于在电源电压低于设定阈值时产生中断或复位。
3. **Low Power Settings**: 用于配置进入 Stop/Standby 模式的选项。

## **HAL 库 PWR 关键 API (RTC & BKP 依赖)**

在 HAL 库中，对 RTC 和 BKP 的操作（写入）必须执行以下两个核心步骤，通常由 HAL 库自动封装或在 `MX_RTC_Init()` 中完成：

### **1. 启动 PWR 时钟 (RCC)**

在任何操作 PWR 或备份域之前，必须确保 PWR 模块的时钟已开启。

C

```
// 确保 PWR 模块的时钟已开启
__HAL_RCC_PWR_CLK_ENABLE(); 
```

### **2. 启用备份域访问 (DBP 位控制)**

这是操作 RTC 和 BKP 寄存器的**必备步骤**。

- **功能**：清除 **DBP** (Disable Backup Protection) 位，打开 RTC 和 BKP 域的写入通道。

C

```
// 启用对备份域的写访问（禁用写保护）
HAL_PWR_EnableBkUpAccess(); 

// ... 执行写入 RTC 或 BKP 的操作 ...

// 禁用对备份域的写访问（重新启用写保护，可选）
HAL_PWR_DisableBkUpAccess();
```

> 注意：
>
> 几乎所有 HAL_RTC_SetTime、HAL_RTC_SetDate、HAL_RTCEx_BKUPWrite 等涉及写入 RTC/BKP 的 HAL 函数，在其内部都会临时调用 HAL_PWR_EnableBkUpAccess() 和 HAL_PWR_DisableBkUpAccess()，因此多数情况下你不需要手动操作。只有当你在 HAL 函数外部直接操作寄存器时才需要注意。

------

## **总结：RTC/BKP/PWR 的联动关系**

| **模块** | **角色**                                    | **关键配置点**                      |
| -------- | ------------------------------------------- | ----------------------------------- |
| **RTC**  | **核心功能**：计时、日历、报警。            | LSE 时钟、预分频器（确保 1 Hz）。   |
| **BKP**  | **数据存储**：存储非易失性数据。            | 读写 `RTC_BKP_DRx` 寄存器。         |
| **PWR**  | **权限管理**：控制对 RTC/BKP 域的写入权限。 | 调用 `HAL_PWR_EnableBkUpAccess()`。 |

# 4. 低功耗模式详解

好的，我为你整理一份关于 **STM32 低功耗模式** 的详细笔记。这份笔记将由浅入深地介绍 STM32 的低功耗原理、各个模式的特性、以及在 **STM32CubeMX 和 HAL 库** 中如何配置和使用。

## **1. 低功耗基础概念与目的**

### **为什么需要低功耗模式？**

在嵌入式系统中，尤其是在电池供电（如物联网设备、可穿戴设备、远程传感器）的应用中，大部分时间芯片处于等待状态。低功耗模式的目的是：

1. **延长电池寿命**：在不执行关键任务时，关闭或降低不必要的时钟和电源，将平均电流降至微安（$\mu\text{A}$）甚至纳安（$\text{nA}$）级别。
2. **保持关键状态**：在深度睡眠时，保留 RAM 中的数据或 RTC（实时时钟）的运行。
3. **快速唤醒**：确保系统能够在需要时（例如，外部事件、定时器中断）快速返回到运行状态。

### **功耗的主要来源**

- **动态功耗**：由晶体管开关引起的功耗，与**时钟频率 ($f$)** 和 **电压 ($V$)** 的平方成正比。$\text{P}_{\text{dynamic}} \propto f \cdot V^2$。这是主动降低时钟频率和工作电压的原因。
- **静态功耗**：由漏电流引起的功耗。这是通过关闭电源域（如进入 Standby 模式）来解决的。

------

## **2. STM32 主要低功耗模式对比**

STM32 的低功耗模式可以根据其功耗深度、唤醒时间和保留的数据分为三大类：

| **模式名称**             | **功耗深度** | **CPU 状态** | **时钟源状态**   | **唤醒时间**               | **典型电流 (μA)** | **保留数据**        |
| ------------------------ | ------------ | ------------ | ---------------- | -------------------------- | ----------------- | ------------------- |
| **Run Mode**             | **最高**     | **执行代码** | 全速运行         | N/A                        | 1000 - 5000       | 所有                |
| **Sleep Mode (C-Sleep)** | 中等         | **停止**     | CPU 时钟停止     | 极快 (0)                   | 1000 - 500        | 所有                |
| **Stop Mode (P-Stop)**   | 低           | 停止         | PLL/HSE/HSI 停止 | 快 ($\sim 5 \mu\text{s}$)  | 5 - 50            | RAM, 寄存器         |
| **Standby Mode**         | **最低**     | 停止         | 所有时钟停止     | 慢 ($\sim 60 \mu\text{s}$) | **< 1**           | **RTC, BKP 寄存器** |

> *注：**C-Sleep** (Core Sleep)，**P-Stop** (Peripheral Stop)。电流值仅为示例，实际值取决于芯片系列和外设配置。*

------

## **3. 各低功耗模式详解与配置**

### **A. Sleep Mode (睡眠模式)**

#### **原理**

仅关闭 **Cortex-M 内核时钟**，所有外设和 SRAM 依然带电运行，时钟保持开启。

#### **唤醒源**

任何启用的中断。

#### **CubeMX/HAL 配置**

1. **配置**：在外设（如 UART、TIM、GPIO EXTI）中配置并启用中断。

2. **HAL API**：

   ```c
   // 进入 Sleep Mode (WFI: Wait For Interrupt)
   HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI); 
   // PWR_MAINREGULATOR_ON: 使用主调压器，快速唤醒。
   // PWR_SLEEPENTRY_WFI: 等待中断。
   ```

### **B. Stop Mode (停止模式)**

### **原理**

在 Sleep 模式的基础上，关闭了高性能时钟（PLL、HSE、HSI）。大部分 SRAM 和所有寄存器内容得以保留。功耗主要由 SRAM 的保持电流决定。

### **唤醒源**

- **EXTI (外部中断)**：任何连接到 EXTI 线的 GPIO 信号。
- **RTC 报警/唤醒**。
- **LSE (低速外部时钟)** 依然可以运行。

### **CubeMX/HAL 配置**

1. **配置**：配置唤醒源（例如，配置 GPIO 为 EXTI 模式并使能 NVIC）。

2. **HAL API**：

   ```c
   // 1. 配置唤醒引脚（如果使用 GPIO/EXTI 唤醒）
   // 2. 进入 Stop Mode
   HAL_PWR_EnterSTOPMode(PWR_MAINREGULATOR_ON, PWR_STOPENTRY_WFI); 
   
   // 3. 唤醒后，需要重新配置系统时钟（PLL/HSE/HSI 已被关闭）
   SystemClock_Config(); 
   ```

### **C. Standby Mode (待机模式)**

#### **原理**

**最深的低功耗模式**。所有电源域都被关闭，**只有** `VBAT` 供电的 RTC 域（包括 RTC 和 BKP 寄存器）保持运行。所有 SRAM 内容和 CPU/外设寄存器内容**全部丢失**。

#### **唤醒源**

唤醒后相当于 **一次复位 (Reset)**。

- **WKUP Pin**：专用的唤醒引脚（如 PA0）。
- **RTC 事件**：RTC 报警或唤醒定时器事件。
- **NRST Pin**：外部复位。
- **IWDG**：独立看门狗复位。

#### **CubeMX/HAL 配置**

1. **CubeMX 配置唤醒源**：

   - **Pinout & Configuration $\rightarrow$ System Core $\rightarrow$ PWR**。
   - **Low Power Settings**：勾选 `WKUP Pin` 或配置 RTC 唤醒。

2. **HAL API**：

   ```c
   // 1. 使能 WKUP 引脚（如果使用）
   HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1_HIGH); 
   
   // 2. 进入 Standby Mode
   HAL_PWR_EnterSTANDBYMode(); 
   
   // **注意**：程序执行到这里后，芯片会立即停止，直到唤醒并复位。
   ```

------

## **4. STM32CubeMX 低功耗配置流程总结**

配置低功耗模式的关键在于**管理时钟和唤醒源**。

### **Step 1: 时钟源选择 (RCC)**

- 如果需要进入 Stop 或 Standby 模式，建议使用 **LSE (32.768 kHz)** 作为 RTC 时钟源，因为它可以在深度睡眠中保持运行，并作为可靠的唤醒定时器。

### **Step 2: 外设配置 (Wakeup Sources)**

- **EXTI/GPIO 唤醒**：配置一个 GPIO 引脚为 **EXTI Mode**，并启用其 NVIC 中断。
- **RTC 唤醒**：配置 RTC 模块，并启用 **Wakeup Timer**，设置周期性唤醒时间。

### **Step 3: 低功耗模式选择 (PWR)**

- **路径**：Pinout & Configuration $\rightarrow$ **System Core** $\rightarrow$ **PWR**。
- 根据目标模式（Stop 或 Standby）配置相关选项（例如，启用 WKUP 引脚）。

### **Step 4: 软件实现 (HAL API)**

在主程序逻辑中，将系统配置好后，调用对应的 `HAL_PWR_EnterXXXXMode()` API 进入休眠。

### **Step 5: 唤醒后的处理**

- **Sleep/Stop Mode**：唤醒后代码从休眠 API 的**下一行**继续执行。在 Stop Mode 唤醒后，**必须**重新调用 `SystemClock_Config()` 恢复系统主时钟。
- **Standby Mode**：唤醒后执行 **冷启动 (Cold Start)**，相当于上电复位，代码从 `main()` 函数的开头执行。通常需要检查 **BKP 寄存器** 或 **RTC 标志位** 来判断是否为 Standby 唤醒。

------

## **5. 深度应用：利用 RTC 唤醒 Standby**

这是最常见的低功耗应用场景：在极低功耗下周期性唤醒，执行任务，然后再次休眠。

### **CubeMX/HAL 步骤**

1. **RTC 配置**：配置 LSE，并计算好 1 Hz 时基。
2. **RTC Wakeup 配置**：
   - 启用 `RTC global interrupt` (NVIC)。
   - 在 RTC 参数中设置 **Wakeup Clock** (如 `RTCCLK/16`)。
3. **Standby 流程代码**：

```c
// Step 1: 检查是否是 RTC 唤醒
if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB) != RESET) {
    // 1. 清除 Standby 标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB); 
    // 2. 清除 RTC 唤醒标志
    __HAL_RTC_WAKEUPTIMER_CLEAR_FLAG(&hrtc, RTC_FLAG_WUTF); 
    // 3. 执行唤醒任务
    printf("Woke up from Standby via RTC!\n");
} else {
    // 首次上电或其他复位
    printf("System Cold Start.\n");
}

// Step 2: 启动 RTC 唤醒定时器（设置 10 秒后唤醒）
HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, 10, RTC_WAKEUPCLOCK_RTCCLK_DIV16);

// Step 3: 配置并进入 Standby Mode
HAL_PWR_EnterSTANDBYMode(); 

// **注意：程序执行到这里就会停止，直到 10 秒后复位，从 main() 重新开始执行**
```