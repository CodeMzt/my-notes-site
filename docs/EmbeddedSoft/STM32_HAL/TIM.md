# 0. 定时器的分类和结构
![](../photosource/基本定时器.png)
![](../photosource/通用定时器.png)
![](../photosource/高级定时器.png)

# **1. 定时器基础参数与时基配置 (Base & Timebase)**

这是所有定时器功能的地基，无论使用 PWM 还是编码器，首先都要配置时基。



## **基本概念**

- **CK_INT**: 内部时钟源频率（通常由 APB1 或 APB2 总线提供，需查阅 Clock Tree）。
  
- **PSC (Prescaler)**: 预分频系数（16位，0~65535）。
  
- **ARR (AutoReload Register)**: 自动重装载值（周期值）。
  
- **CNT (Counter)**: 当前计数值。
  

## **CubeMX 配置细节**

1. **Pinout & Configuration**: 选择 TIMx。
   
2. **Clock Source**: 选择 `Internal Clock` (通常情况)。
   
3. **Parameter Settings**:
   
    - **Prescaler (PSC)**: 输入 $N-1$。例如分频 72，输入 `71`。
      
    - **Counter Mode**: `Up` (向上计数) 最常用。
      
    - **Counter Period (ARR)**: 输入 $M-1$。决定了溢出/更新的时间点。
      
    - **Internal Clock Division (CKD)**: 数字滤波器使用的采样时钟分频，通常选 `No Division`。
      
    - **Auto-reload preload**: `Enable` (建议开启，使修改 ARR 在下个更新事件生效，防止波形错乱)。
      

> 核心公式:
> 
> $$\text{溢出频率} = \frac{\text{CK\_INT}}{(PSC+1) \times (ARR+1)}$$
> 
> $$\text{溢出时间} = \frac{(PSC+1) \times (ARR+1)}{\text{CK\_INT}}$$

---

# **2. 定时中断 (Timer Interrupt)**

最基础的功能，用于周期性执行任务。
![](../photosource/定时中断结构.png)

## **CubeMX 配置细节**

1. **配置时基**: 如上所述，计算好 PSC 和 ARR 以获得目标中断频率（例如 1ms 或 1s）。
   
2. **NVIC Settings**:
   
    - **Enabled**: **必须勾选** `TIMx global interrupt`。
      
    - **Preemption Priority**: 根据系统实时性要求设置优先级。
      

## **代码实现**

- **启动**:
  
    ```c
    // 在 main.c 的 user code begin 2
    HAL_TIM_Base_Start_IT(&htim2); // 启动定时器并开启更新中断
    ```
    
- **回调函数**:
  
    ```c
    // 在 main.c 或任意源文件中重写
    void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
    {
        if (htim->Instance == TIM2) {
            // 执行周期性任务，例如 1ms 一次
            // 注意：不要在此执行耗时操作（如 printf 延迟）
        }
    }
    ```
    

---

# **3. PWM 输出 (Pulse Width Modulation)**

基于 **4.输出比较** 实现， 用于电机调速、LED 呼吸灯、蜂鸣器驱动。

## **CubeMX 配置细节**

1. **Mode**: 在 Pinout 中将 Channel x 选为 `PWM Generation CHx`。
   
2. **Configuration -> Parameter Settings**:
   
    - **Counter Settings**: 配置 PSC 和 ARR 决定 **PWM 频率**。
      
    - **PWM Generation Channel x**:
      
        - **Mode**:
          
            - `PWM mode 1` (常用): CNT < CCR 时有效。
              
            - `PWM mode 2`: CNT > CCR 时有效。
            
        - **Pulse (CCR)**: 初始占空比数值。$\text{Duty} = \frac{CCR}{ARR+1}$。
          
        - **Output compare preload**: `Enable` (重要，防止修改占空比时产生毛刺)。
          
        - **CH Polarity**: `High` (有效电平为高) 或 `Low`。
          

## **代码实现**

- **启动**:
  
    ```c
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1); // 开启 PWM 输出
    ```
    
- **运行时修改占空比**:
  
    ```c
    // 修改 CCR 寄存器，范围 0 ~ ARR
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 500);
    ```
    

---

# **4. 输出比较 (Output Compare - OC)**

输出比较可以通过比较CNT与CCR寄存器值的关系，来对输出电平进行置1、置0或翻转的操作，用于输出一定频率和占空比的PWM波形

与 PWM 类似但更灵活，用于生成精确的脉冲、相位控制或在特定时间翻转电平（Toggle）。**它不强制要求连续波形。**

## **CubeMX 配置细节**

1. **Mode**: 将 Channel x 选为 `Output Compare CHx`。
   
2. **Configuration -> Parameter Settings**:
   
    - **Output Compare Channel x**:
      
        - **Mode**:
          
            - `Toggle on match`: CNT == CCR 时翻转引脚电平（常用，生成固定频率方波，频率为溢出频率的一半）。
              
            - `Set active on match`: 匹配时置高。
              
            - `PWM mode`: 其实 OC 也可以配成 PWM，但功能少于专用 PWM 模式。
            
        - **Pulse**: 初始比较值。
    
3. **NVIC Settings**: 如果需要在匹配时触发中断处理（例如相位控制），需要开启 NVIC。
   

## **代码实现**

- **启动**:

    ```c
    // 方式1: 仅输出电平，不进中断
    HAL_TIM_OC_Start(&htim3, TIM_CHANNEL_1);
    
    // 方式2: 开启输出并开启匹配中断
    HAL_TIM_OC_Start_IT(&htim3, TIM_CHANNEL_1);
    ```
    
- **中断回调 (如果开启了 IT)**:
  
    ```c
    void HAL_TIM_OC_DelayElapsedCallback(TIM_HandleTypeDef *htim)
    {
        if(htim->Channel == HAL_TIM_ACTIVE_CHANNEL_1) {
            // 匹配事件发生，可以在此动态修改下一次的 CCR 值以改变相位
            uint32_t current_ccr = __HAL_TIM_GET_COMPARE(htim, TIM_CHANNEL_1);
            __HAL_TIM_SET_COMPARE(htim, TIM_CHANNEL_1, current_ccr + offset);
        }
    }
    ```
    

---

# **5. 输入捕获 (Input Capture - IC)**

输入捕获模式下，当通道输入引脚出现指定电平跳变时，当前CNT的值将被锁存到CCR中，可用于测量PWM波形的频率、占空比、脉冲间隔、电平持续时间等参数

用于测量外部信号的脉宽、周期、频率。

## **CubeMX 配置细节**

1. **Mode**: Channel x 选为 `Input Capture direct mode`。
   
2. **Configuration -> Parameter Settings**:
   
    - **Counter Settings**: 配置 PSC 使得定时器不那么快溢出，但精度又要足够。
      
    - **Input Capture Channel x**:
      
        - **Polarity**: `Rising Edge` (上升沿) 或 `Falling Edge` (下降沿)。
          
        - **Selection**: `Direct` (TI1映射到IC1)。
          
        - **Prescaler**: 这里的预分频是对输入信号的分频（例如每8个沿捕获一次），测高频时有用，通常选 `No prescaler`。
          
        - **Input Filter**: `0`~`15`，数字滤波，滤除输入信号毛刺。
    
3. **NVIC Settings**: **必须开启** `TIMx global interrupt`。
   

## **代码实现**

- **启动**:
  
    ```c
    HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_1);
    ```
    
- **测量逻辑 (回调函数)**:
  
    ```c
    uint32_t val1 = 0, val2 = 0;
    uint8_t capture_idx = 0;
    
    void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
    {
        if (htim->Instance == TIM2 && htim->Channel == HAL_TIM_ACTIVE_CHANNEL_1)
        {
            if (capture_idx == 0) {
                val1 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
                capture_idx = 1;
            } else {
                val2 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
                // 处理溢出逻辑（如果 val2 < val1，说明中间发生过 ARR 溢出）
                // 计算周期 = val2 - val1 (需考虑溢出补偿)
                capture_idx = 0; 
            }
        }
    }
    ```
    

---

# **6. 组合通道 (Combined Channels) 与 PWM 输入模式**

CubeMX 中的 `Combined Channels` 选项通常用于特殊的硬件绑定功能，最典型的是 **PWM Input Mode**（同时测量频率和占空比）或 **Encoder Mode**、**Hall Sensor Mode**。

以 **PWM Input Mode** 为例（这是一个非常强大的功能，用一个定时器引脚同时捕获周期和脉宽）：

## **CubeMX 配置细节**

1. **Mode**:
   
    - **Slave Mode**: `Reset Mode` (复位模式)。
      
    - **Trigger Source**: `TI1FP1` (假设信号从 CH1 进)。
      
    - **Combined Channels**: 勾选 `PWM Input on CH1` (CubeMX 会自动把 CH2 变成 Indirect mode)。
    
2. **Configuration**:
   
    - **Channel 1 (IC1)**: Polarity `Rising Edge` (测周期)，Selection `Direct`。
      
    - **Channel 2 (IC2)**: Polarity `Falling Edge` (测占空比)，Selection `Indirect`。
      
    - **原理**: 上升沿触发 Reset（CNT清零）并由 IC1 捕获（此时是0，但下个周期就是周期值），下降沿由 IC2 捕获（此时是脉宽值）。
      

## **代码实现**


```c
// 启动 PWM 输入捕获（需要同时启动两个通道）
HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_1);
HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_2);

// 在回调中读取
uint32_t IC1_Value = HAL_TIM_ReadCapturedValue(&htim2, TIM_CHANNEL_1); // 周期 (Frequency)
uint32_t IC2_Value = HAL_TIM_ReadCapturedValue(&htim2, TIM_CHANNEL_2); // 脉宽 (Duty)
if (IC1_Value != 0) {
    float duty = (float)IC2_Value / IC1_Value * 100;
}
```

---

# **7. 编码器模式 (Encoder Mode)**

用于读取旋转编码器（AB相）的信号，自动处理正反转。

## **CubeMX 配置细节**

1. **Mode**:
   
    - **Combined Channels**: `Encoder Mode`。
    
2. **Configuration -> Parameter Settings**:
   
    - **Encoder Mode**:
      
        - `Encoder Mode TI1 and TI2`: **4倍频模式** (精度最高，上下沿都计数)。
          
        - `Encoder Mode TI1`: 2倍频。
        
    - **Counter Period (ARR)**: 通常设为最大 `65535` (16bit) 或 `4294967295` (32bit)，防止过快溢出。
      
    - **Input Filter**: 建议设为 `10` 或更高，防止机械抖动误判。
    
3. **NVIC**: 通常**不需要**开启中断，除非你要计算多圈绝对位置（处理溢出）。
   

## **代码实现**

- **启动**:
  
    ```c
    HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
    ```
    
- **读取数据 (轮询)**:
  
    ```c
    // int16_t 强转是为了处理反转时的负数（补码）
    int16_t speed = (int16_t)__HAL_TIM_GET_COUNTER(&htim3); 
    
    // 读取后通常需要清零 CNT 以测量速度（单位时间内的脉冲数）
    __HAL_TIM_SET_COUNTER(&htim3, 0);
    
    // 如果是测绝对位置，则不清零，需处理溢出逻辑
    ```
    

---

# **8. 触发源 (Trigger Source) 与主从模式**

这是 STM32 定时器的灵魂功能，允许硬件自动同步，无需 CPU 干预。

## **基本概念**

- **ITR (Internal Trigger)**: 内部触发，定时器级联（如 TIM1 溢出触发 TIM2 启动）。
  
- **ETR (External Trigger)**: 外部引脚触发。
  
- **TIxFPx**: 输入捕获引脚信号作为触发源。
  

## **常见应用场景：TIM1 主控 TIM2 (级联)**

- **Master (TIM1) 配置**:
  
    - **Trigger Output (TRGO)**: `Update Event` (当 TIM1 发生更新/溢出时发送信号)。
    
- **Slave (TIM2) 配置**:
  
    - **Slave Mode**: `External Clock Mode 1` (外部时钟模式，即 TIM2 计数器的驱动不是内部晶振，而是 TIM1 的溢出脉冲)。
      
    - **Trigger Source**: `ITR0` (查阅手册，ITR0 对应 TIM1)。
    
- **NVIC**: 都不需要开中断，硬件全自动。
  

## **常见应用场景：外部引脚控制启停 (Gated Mode)**

- **Slave (TIMx) 配置**:
  
    - **Slave Mode**: `Gated Mode`。
      
    - **Trigger Source**: `TI1FP1` (CH1 引脚)。
      
    - **效果**: 当 CH1 为高电平时，定时器计数；低电平时，定时器暂停。
      

## **代码实现**

大部分配置在 MX_TIMx_Init 中自动生成 (HAL_TIM_SlaveConfigSynchro)。

用户只需启动定时器：
	
```c
HAL_TIM_Base_Start(&htim1); // 启动主定时器
HAL_TIM_Base_Start(&htim2); // 启动从定时器
```

---

# **9. 使用了 CubeMX 后你不用关心的细节**

1. 时钟使能 (__HAL_RCC_TIMx_CLK_ENABLE):
   
    CubeMX 自动在 stm32fxxx_hal_msp.c 的 HAL_TIM_Base_MspInit 中生成。
    
2. GPIO 复用映射 (AF):
   
    CubeMX 自动配置 GPIO 的 Alternate Function 寄存器（如将 PA6 复用为 TIM3_CH1）。
    
3. 中断清除:
   
    HAL 库的通用中断处理函数 HAL_TIM_IRQHandler 会自动读取并清除 SR 寄存器的标志位，然后才调用你的 Callback。不要在 Callback 里手动清除标志位，否则可能导致逻辑错误。
    
4. 结构体初始化:
   
    TIM_HandleTypeDef、TIM_OC_InitTypeDef 等繁琐的结构体赋值全部自动化。
    

---

# **10. 常用 API 速查表**

|**功能**|**API**|**备注**|
|---|---|---|
|**启动/停止 (无中断)**|`HAL_TIM_Base_Start`, `HAL_TIM_Base_Stop`|基本计数|
|**启动/停止 (带中断)**|`HAL_TIM_Base_Start_IT`, `HAL_TIM_Base_Stop_IT`|周期任务|
|**PWM 操作**|`HAL_TIM_PWM_Start`, `__HAL_TIM_SET_COMPARE`|调速/调光|
|**输入捕获**|`HAL_TIM_IC_Start_IT`, `HAL_TIM_ReadCapturedValue`|测频/测宽|
|**编码器**|`HAL_TIM_Encoder_Start`, `__HAL_TIM_GET_COUNTER`|测速/位置|
|**设置 CNT**|`__HAL_TIM_SET_COUNTER(&htimx, value)`|修正计数值|
|**设置 ARR**|`__HAL_TIM_SET_AUTORELOAD(&htimx, value)`|动态改周期|
# 11. RCC时钟树
 ![](../photosource/RCC时钟树.jpg)