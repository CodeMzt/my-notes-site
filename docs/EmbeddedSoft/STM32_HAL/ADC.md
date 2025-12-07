# 1. ADC基础概念

## 1.1 ADC工作原理

模数转换器（ADC）将模拟信号转换为数字信号，STM32的ADC通常是逐次逼近型。

## 1.2 主要参数

- **分辨率**: 12位（0-4095）
  
- **采样时间**: 可配置，影响转换精度
  
- **参考电压**: VREF+ 和 VREF-
  
- **转换模式**: 单次、连续、扫描、间断
# 2.配置说明
## 1.1 步骤
1. 选择通道值
2. 选择ADC1或ADC2
3. 进入对应ADC配置界面进行配置
## 1.2 参数说明
### 工作模式
![](../photosource/ADC配置1.png)

#### 独立模式 vs 多ADC模式

##### 独立模式 (Independent mode)
- **描述**: 单个ADC独立工作，不与其他ADC交互
- **应用场景**: 简单的单通道或多通道采样需求
- **配置方法**:
```c
hadc1.Init.ScanConvMode = DISABLE;  // 单通道
// 或
hadc1.Init.ScanConvMode = ENABLE;   // 多通道扫描
```

##### 双ADC组合模式 (Dual ADC modes)

###### 1. 组合规则同步模式 (Combined Regular Simultaneous Mode)
- **工作原理**: 两个ADC同时采样不同的通道，转换同步进行
- **优势**: 提高采样吞吐量，同时获取多个信号
- **典型应用**: 需要同步采样的多路信号
```c
// ADC1和ADC2同时采样不同通道
// 转换结果分别存储
```

###### 2. 交替模式 (Interleaved Mode)
- **工作原理**: 两个ADC交替对同一通道进行采样
- **优势**: 有效提高采样率（几乎翻倍）
- **时序**: ADC1采样 → ADC1转换 → ADC2采样 → ADC2转换
```c
// 适用于高频信号采集
// 采样率 = 2 × 单个ADC采样率
```

###### 3. 交替触发模式 (Alternate Trigger Mode)
- **工作原理**: 使用外部触发信号交替触发两个ADC
- **优势**: 精确控制采样时序
- **应用**: 需要严格时序控制的应用

###### 4. 组合注入同步模式 (Combined Injected Simultaneous Mode)
- **工作原理**: 两个ADC同步执行注入组转换
- **优势**: 高优先级信号的同步采集
- **应用**: 紧急事件处理、关键参数监测

###### 5. 看门狗模式 (Watchdog Mode)
- **工作原理**: 监控特定ADC通道，当数值超出设定范围时触发中断
- **配置示例**:
```c
ADC_AnalogWDGConfTypeDef AnalogWDGConfig;
AnalogWDGConfig.WatchdogNumber = ADC_ANALOGWATCHDOG_1;
AnalogWDGConfig.Channel = ADC_CHANNEL_0;
AnalogWDGConfig.ITMode = ENABLE;
AnalogWDGConfig.HighThreshold = 3000;
AnalogWDGConfig.LowThreshold = 1000;
HAL_ADC_AnalogWDGConfig(&hadc1, &AnalogWDGConfig);
```

#### 扫描模式 (Scan Mode)

##### 单次扫描
- **行为**: 配置的所有通道按顺序转换一次后停止
- **配置**:
```c
hadc1.Init.ScanConvMode = ENABLE;
hadc1.Init.ContinuousConvMode = DISABLE;
```

##### 连续扫描  
- **行为**: 配置的所有通道循环连续转换
- **配置**:
```c
hadc1.Init.ScanConvMode = ENABLE;
hadc1.Init.ContinuousConvMode = ENABLE;
```

#### 转换模式

##### 单次转换模式 (Single Conversion)
- **工作流程**: 启动 → 转换指定通道 → 停止
- **适用场景**: 低速、低功耗应用
```c
hadc1.Init.ContinuousConvMode = DISABLE;
HAL_ADC_Start(&hadc1);  // 每次都需要重新启动
```

##### 连续转换模式 (Continuous Conversion)  
- **工作流程**: 启动后自动连续转换，无需重复触发
- **适用场景**: 高速数据采集
```c
hadc1.Init.ContinuousConvMode = ENABLE;
HAL_ADC_Start(&hadc1);  // 启动后持续运行
```

#### 触发模式

##### 软件触发
- **控制方式**: 通过代码控制转换开始
- **灵活性**: 高，可精确控制采样时刻
```c
hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
HAL_ADC_Start(&hadc1);  // 软件启动
```

##### 硬件触发
- **触发源**: 定时器、外部引脚等
- **优势**: 精确的定时采样，不依赖CPU
```c
// 使用TIM1触发ADC转换
hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIGCONV_T1_TRGO;
```

#### 数据管理模式

##### 轮询模式 (Polling)
```c
HAL_ADC_Start(&hadc1);
HAL_ADC_PollForConversion(&hadc1, timeout);
value = HAL_ADC_GetValue(&hadc1);
```

##### 中断模式 (Interrupt)
```c
HAL_ADC_Start_IT(&hadc1);
// 在回调函数中处理数据
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
```

##### DMA模式 (Direct Memory Access)
- **优势**: 不占用CPU，高效处理大量数据
- **配置**:
```c
// 单次DMA传输
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)buffer, length);

// 循环DMA传输（需配置DMA为循环模式）
```

#### 注入组 vs 规则组

##### 规则组 (Regular Group)
- **优先级**: 普通
- **通道数量**: 最多16个通道
- **触发方式**: 软件或硬件触发
- **典型应用**: 常规数据采集

##### 注入组 (Injected Group)
- **优先级**: 高（可中断规则组转换）
- **通道数量**: 最多4个通道  
- **触发方式**: 自动或外部触发
- **典型应用**: 紧急事件处理、关键参数

```c
// 配置注入组
ADC_InjectionConfTypeDef sConfigInjected;
sConfigInjected.InjectedNbrOfConversion = 2;
sConfigInjected.InjectedChannel = ADC_CHANNEL_1;
sConfigInjected.InjectedRank = 1;
HAL_ADCEx_InjectedConfigChannel(&hadc1, &sConfigInjected);
```

#### 低功耗模式

##### 自动延迟模式 (Auto-delay)
- **功能**: 在转换间插入延迟以降低功耗
- **适用**: 对采样率要求不高的应用

##### 间断模式 (Discontinuous Mode)
- **工作方式**: 每次触发只转换指定数量的通道
- **节能效果**: 减少不必要的转换操作

#### 模式选择指南

| 应用场景    | 推荐模式              | 理由          |
| ------- | ----------------- | ----------- |
| 简单单通道采样 | 独立模式 + 轮询         | 实现简单，资源占用少  |
| 高速数据采集  | 独立模式 + DMA + 连续转换 | 高吞吐量，CPU占用低 |
| 同步多路信号  | 组合规则同步模式          | 同时采集，数据相关性好 |
| 超高频信号   | 交替模式              | 有效提升采样率     |
| 关键参数监控  | 看门狗模式 + 注入组       | 实时监控，快速响应   |
| 定时精确采样  | 硬件触发模式            | 时序精确，不依赖软件  |

#### 配置注意事项

1. **时钟配置**: 确保ADC时钟不超过器件最大频率
2. **采样时间**: 根据信号源阻抗调整采样时间
3. **DMA配置**: 多ADC模式需要合理配置DMA数据流
4. **中断优先级**: 注入组中断应设置为较高优先级
5. **电源噪声**: 模拟部分供电需要良好的去耦设计
### 基本设置
![](../photosource/ADC配置2.png)
#### 数据对齐
左对齐或右对齐
#### 扫描模式
是否对多通道扫描
#### 连续转换模式
是否启用连续转换
### 规则组设置
![](../photosource/ADC配置3.png)
- **Number Of Conversion:** 每次转换多少通道。若此值大于1，最好配合DMA，因为规则组转换完成存储数据的寄存器只有一个，后来的会覆盖前面的数据。
- **External Trigger Conversion Source:** 选择转换触发源：软件 or 硬件（定时器）
- **Rank&Channel&SampleTIme:** 配置对应通道转换的序号以及采样率[^1]

[^1]: **SampleTime 1.5 Cycles** 指的是ADC对输入信号进行采样的时间长度为**1.5个ADC时钟周期**。
### 注入组设置&开门狗启用
![](../photosource/ADC配置4.png)
### 中断设置（NVIC）
#### 中断的基本概念

ADC全局中断用于在特定ADC事件发生时通知CPU，实现异步事件处理，避免轮询等待。
#### 主要中断事件类型

```c
// ADC常见中断事件
#define ADC_IT_EOC      ((uint32_t)ADC_IER_EOCIE)      // 转换完成中断
#define ADC_IT_JEOC     ((uint32_t)ADC_IER_JEOCIE)     // 注入组转换完成
#define ADC_IT_AWD      ((uint32_t)ADC_IER_AWDIE)      // 模拟看门狗中断
#define ADC_IT_OVR      ((uint32_t)ADC_IER_OVRIE)      // 溢出中断
```
## 用户实现
### 自校准
需要在cubemx生成的adc.c中ADC初始化函数补充(例adc1)
```c
/* USER CODE BEGIN ADC1_Init 2 */  
//自校准  
if (HAL_ADCEx_Calibration_Start(&hadc1)!= HAL_OK)  
{  
  Error_Handler();  
}  
/* USER CODE END ADC1_Init 2 */
```
### 读取特定通道值（独立单次非扫描,adc2）
```c
ADC_ChannelConfTypeDef sConfig = {0};
sConfig.Channel = ADC_CHANNEL_2;//配置对应通道到首位
sConfig.Rank = ADC_REGULAR_RANK_1;  
sConfig.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;  
if (HAL_ADC_ConfigChannel(&hadc2, &sConfig) != HAL_OK)  
{  
  Error_Handler();  
}  
// 启动ADC转换  
if (HAL_ADC_Start(&hadc2) == HAL_OK)  
{  
  // 等待转换完成  
  if (HAL_ADC_PollForConversion(&hadc2, 100) == HAL_OK)  
  {  
    return HAL_ADC_GetValue(&hadc2);  
  }  
}  
Error_Handler();
```