[TOC]
# 中断基础概念

## 什么是中断

中断是处理器响应外部事件的一种机制，当外设需要CPU处理时，会通过中断信号通知CPU。

## 中断类型

- **硬件中断**：由外设产生（定时器、串口、GPIO等）
  
- **软件中断**：由软件指令触发

## 中断处理过程

1. 保存当前执行上下文
2. 跳转到中断服务程序（ISR）
3. 执行ISR中的处理逻辑
4. 恢复上下文并返回
# 中断和异常的区别
## 比喻：公司运营
把CPU想象成一家公司的**CEO**。

- **中断 (Interrupt)** = **外部来电**
  - 来自公司外部：客户、供应商、政府机构
  - 优先级相对较低，CEO可以说“稍等，我处理完内部事务再接”
  - 例子：USB设备插入、网络数据到达、按键按下

- **异常 (Exception)** = **内部紧急会议**
  - 来自公司内部：财务危机、法律诉讼、系统崩溃
  - 优先级很高，CEO必须立即处理
  - 例子：除零错误、内存访问违规、系统调用

##  技术层面的区别

| 特性 | **中断 (Interrupt)** | **异常 (Exception)** |
|------|---------------------|---------------------|
| **来源** | 外部硬件设备 | CPU内部执行指令时产生 |
| **同步性** | 异步（随时可能发生） | 同步（特定指令必然触发） |
| **可预测性** | 不可预测 | 相对可预测 |
| **处理优先级** | 相对较低 | 相对较高 |
| **例子** | 定时器、UART、GPIO | 除零、内存错误、SVC指令 |

## 为什么叫“系统异常”？

**系统异常**是异常的一个子类，特指那些**用于操作系统核心功能的异常**：

```c
// 这些就是ARM Cortex-M的主要系统异常：
Reset_Handler        // 复位
NMI_Handler          // 不可屏蔽中断  
HardFault_Handler    // 硬件错误
MemManage_Handler    // 内存管理错误
BusFault_Handler     // 总线错误
UsageFault_Handler   // 指令使用错误
SVC_Handler          // 系统调用 ← 就是这个！
DebugMon_Handler     // 调试监控
PendSV_Handler       // 可挂起的系统调用
SysTick_Handler      // 系统定时器
```

## “异常在哪？”- 异常的实际位置

在ARM Cortex-M中，异常和中断都在同一个地方——**异常向量表**：

```assembly
// 在内存开始的位置（通常是0x00000000）
Vector_Table:
    .long   __StackTop         /* 栈顶 */
    .long   Reset_Handler      /* 复位异常 */
    .long   NMI_Handler        /* NMI异常 */
    .long   HardFault_Handler  /* 硬件错误异常 */
    // ... 更多系统异常
    .long   SVC_Handler        /* 系统调用异常 ← 就在这里！*/
    // ... 然后是外设中断
    .long   TIM2_IRQHandler    /* 定时器2中断 */
    .long   USART1_IRQHandler  /* 串口1中断 */
```

## 为什么RTOS要用SVC异常？

看这个例子就明白了：

```c
// 用户代码调用OS API
osThreadNew(my_function, NULL, NULL);

// 编译后实际上：
BL osThreadNew        // 跳转到OS函数
  ↓ (在OS函数内部)
SVC 0x03             // 触发SVC异常，进入特权模式
  ↓
SVC_Handler()        // 异常处理程序执行真正的系统功能
```

**关键好处**：
- 用户代码在非特权模式下运行，无法直接访问关键硬件
- 通过SVC异常“敲门”，让操作系统在特权模式下代为执行
- 提供了安全边界，防止用户程序破坏系统

## 总结

- **中断**：外部硬件“打扰”CPU
- **异常**：CPU自己执行指令时“出状况”或“需要特权”
- **系统异常**：操作系统专用的特殊异常机制
- **SVC**：是应用程序向操作系统请求服务的“安全门”

异常就像是CPU的“内部紧急处理机制”，而中断是“外部打扰机制”。
# FreeRTOS中断优先级分组

## 优先级数值规则

- **数值越小，优先级越高**
- 不同Cortex-M芯片支持的优先级位数不同（STM32为4位，0~15优先级）

## Cortex-M 优先级分组机制

### 优先级分组原理

Cortex-M处理器使用优先级分组寄存器来划分抢占优先级和子优先级：

```c
// 优先级分组配置（8位优先级寄存器示例）
// 分组0: 7位抢占优先级，1位子优先级  [7:1]抢占, [0:0]子优先级
// 分组1: 6位抢占优先级，2位子优先级  [7:2]抢占, [1:0]子优先级  
// 分组2: 5位抢占优先级，3位子优先级  [7:3]抢占, [2:0]子优先级
// 分组3: 4位抢占优先级，4位子优先级  [7:4]抢占, [3:0]子优先级
// 分组4: 3位抢占优先级，5位子优先级  [7:5]抢占, [4:0]子优先级
// 分组5: 2位抢占优先级，6位子优先级  [7:6]抢占, [5:0]子优先级
// 分组6: 1位抢占优先级，7位子优先级  [7:7]抢占, [6:0]子优先级
// 分组7: 0位抢占优先级，8位子优先级  无抢占, [7:0]子优先级
```

## FreeRTOS 中断优先级配置

### FreeRTOSConfig.h 关键配置

```c
// FreeRTOSConfig.h 中的中断配置

/*  Cortex-M 特定配置  */

// 最低中断优先级（数值越大优先级越低）
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY    15

// 允许调用FreeRTOS API的最高中断优先级
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY 5

// 内核可管理的中断优先级（自动计算），__NVIC_PRIO_BITS应该设为4，即group4
#define configMAX_SYSCALL_INTERRUPT_PRIORITY \
    (configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << (8 - __NVIC_PRIO_BITS))

// 系统节拍器中断优先级
#define configKERNEL_INTERRUPT_PRIORITY \
    (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << (8 - __NVIC_PRIO_BITS))

// PendSV 中断优先级  
#define configPEND_SV_INTERRUPT_PRIORITY \
    (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << (8 - __NVIC_PRIO_BITS))

// 系统节拍频率（Hz）
#define configTICK_RATE_HZ 1000
```

### FreeRTOS 中断优先级层次结构

#### 高于configMAX_SYSCALL_INTERRUPT_PRIORITY

 * 不能调用FreeRTOS API，用于紧急中断，高于一切任务

#### 低于configMAX_SYSCALL_INTERRUPT_PRIORITY  

 * 可以调用FreeRTOS API FromISR函数

#### 优先级15:    最低优先级

- 用于SysTick（心脏）和PendSV（调度）

# 临界段（Critical Section）

## 临界段基本概念

**临界段**（Critical Section）是指必须**原子性执行**的代码段，在这段代码执行期间不能被打断，必须保证其执行的完整性和一致性。

## 代码保护

代码会被**中断**、调度打断，但临界段不能被打断，因此我们有相应的**代码保护**措施。它们通过**中断屏蔽**实现。

## 中断屏蔽基础概念

### 什么是中断屏蔽

中断屏蔽是通过设置特定寄存器来暂时禁止处理器响应中断的机制：

 中断屏蔽的主要目的：

1. 保护**临界区代码**
2. 防止数据竞争
3. 确保操作的原子性
4. 避免任务切换在关键时期发生

### 屏蔽用途

| 屏蔽级别       | 控制寄存器 | 作用范围             | 使用场景     |
| :------------- | :--------- | :------------------- | :----------- |
| **全局屏蔽**   | PRIMASK    | 所有可屏蔽异常       | 最严格的保护 |
| **优先级屏蔽** | BASEPRI    | 低于指定优先级的中断 | FreeRTOS常用 |
| **故障屏蔽**   | FAULTMASK  | 所有异常（包括故障） | 故障处理     |

### 寄存器说明

| 寄存器        | 位宽 | 复位值 | 屏蔽范围               | 典型应用场景   |
| :------------ | :--- | :----- | :--------------------- | :------------- |
| **PRIMASK**   | 1位  | 0      | 所有可屏蔽异常         | 短时间全局保护 |
| **BASEPRI**   | 8位  | 0      | 优先级低于设定值的异常 | FreeRTOS临界区 |
| **FAULTMASK** | 1位  | 0      | 所有异常(除NMI)        | 故障处理       |

> [!Note]
>
> 上面说的只是为了帮助理解原理，实际上FreeRTOS已经帮我们配好了，不用我们自己操作寄存器。我们需要屏蔽时，FreeRTOS有提供中断管理API函数。

## 中断屏蔽控制 API

### FreeRTOS

#### 底层

```c
/*=== 底层中断控制 ===*/

// 全局中断禁用/启用
void portDISABLE_INTERRUPTS(void);
void portENABLE_INTERRUPTS(void);

// 特定优先级中断屏蔽
UBaseType_t ulPortSetInterruptMask(void); // 进入屏蔽，返回原状态，之后可以设置新的优先级屏蔽
void vPortClearInterruptMask(UBaseType_t ulNewMask);  // 退出屏蔽，恢复状态
```

#### 应用层

```c
/*=== 顶层API实现 ===*/
//优先级中断屏蔽，即屏蔽可管控的优先级区间（比如15~5）,用于临界段代码保护
void taskENTER_CRITICAL();//内部调用portDISABLE_INTERRUPTS
void taskEXIT_CRITICAL();//内部调用portENABLE_INTERRUPTS

//优先级中断屏蔽，即屏蔽可管控的优先级区间（比如15~5）,用于中断内临界段代码保护
UBaseType_t taskENTER_CRITICAL_FROM_ISR();//ulPortSetInterruptMask
void taskEXIT_CRITICAL_FROM_IS(UBaseType_t save_status);//vPortClearInterruptMask

// 上下文切换触发
void portYIELD_FROM_ISR(BaseType_t xHigherPriorityTaskWoken);//中断中使用
void portYIELD(void);//正常函数使用
```

### CMSIS v2

#### 底层

```c
#include "cmsis_compiler.h"
#include "core_cm4.h"
/*=== 全局中断控制 ===*/

// 启用全局中断
__STATIC_FORCEINLINE void __enable_irq(void)
{
    __asm volatile ("cpsie i" : : : "memory");
}

// 禁用全局中断  
__STATIC_FORCEINLINE void __disable_irq(void)
{
    __asm volatile ("cpsid i" : : : "memory");
}

// 启用故障中断
__STATIC_FORCEINLINE void __enable_fault_irq(void)
{
    __asm volatile ("cpsie f" : : : "memory");
}

// 禁用故障中断
__STATIC_FORCEINLINE void __disable_fault_irq(void)
{
    __asm volatile ("cpsid f" : : : "memory");
}

/*=== 优先级屏蔽控制 ===*/

// 设置 BASEPRI 寄存器
__STATIC_FORCEINLINE void __set_BASEPRI(uint32_t basePri)
{
    __asm volatile ("MSR basepri, %0" : : "r" (basePri) : "memory");
}

// 获取 BASEPRI 寄存器值
__STATIC_FORCEINLINE uint32_t __get_BASEPRI(void)
{
    uint32_t result;
    __asm volatile ("MRS %0, basepri" : "=r" (result));
    return result;
}

// 设置 FAULTMASK 寄存器
__STATIC_FORCEINLINE void __set_FAULTMASK(uint32_t faultMask)
{
    __asm volatile ("MSR faultmask, %0" : : "r" (faultMask) : "memory");
}

// 获取 FAULTMASK 寄存器值
__STATIC_FORCEINLINE uint32_t __get_FAULTMASK(void)
{
    uint32_t result;
    __asm volatile ("MRS %0, faultmask" : "=r" (result));
    return result;
}
```

#### NVIC 中断控制器 API

```c
#include "core_cm4.h"

/*=== 中断使能控制 ===*/

// 使能特定中断
__STATIC_FORCEINLINE void NVIC_EnableIRQ(IRQn_Type IRQn)
{
    NVIC->ISER[(((uint32_t)IRQn) >> 5UL)] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
}

// 禁用特定中断
__STATIC_FORCEINLINE void NVIC_DisableIRQ(IRQn_Type IRQn)
{
    NVIC->ICER[(((uint32_t)IRQn) >> 5UL)] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
}

// 获取中断使能状态
__STATIC_FORCEINLINE uint32_t NVIC_GetEnableIRQ(IRQn_Type IRQn)
{
    return ((uint32_t)(((NVIC->ISER[(((uint32_t)IRQn) >> 5UL)] & (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
}

/*=== 中断优先级控制 ===*/

// 设置中断优先级
__STATIC_FORCEINLINE void NVIC_SetPriority(IRQn_Type IRQn, uint32_t priority)
{
    NVIC->IP[((uint32_t)IRQn)] = (uint8_t)((priority << (8U - __NVIC_PRIO_BITS)) & (uint32_t)0xFFUL);
}

// 获取中断优先级
__STATIC_FORCEINLINE uint32_t NVIC_GetPriority(IRQn_Type IRQn)
{
    return ((uint32_t)(((NVIC->IP[((uint32_t)IRQn)] >> (8U - __NVIC_PRIO_BITS)) & (uint32_t)0x03UL)));
}

/*=== 中断挂起控制 ===*/

// 设置中断挂起
__STATIC_FORCEINLINE void NVIC_SetPendingIRQ(IRQn_Type IRQn)
{
    NVIC->ISPR[(((uint32_t)IRQn) >> 5UL)] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
}

// 清除中断挂起
__STATIC_FORCEINLINE void NVIC_ClearPendingIRQ(IRQn_Type IRQn)
{
    NVIC->ICPR[(((uint32_t)IRQn) >> 5UL)] = (uint32_t)(1UL << (((uint32_t)IRQn) & 0x1FUL));
}

// 获取中断挂起状态
__STATIC_FORCEINLINE uint32_t NVIC_GetPendingIRQ(IRQn_Type IRQn)
{
    return ((uint32_t)(((NVIC->ISPR[(((uint32_t)IRQn) >> 5UL)] & (1UL << (((uint32_t)IRQn) & 0x1FUL))) != 0UL) ? 1UL : 0UL));
}
```

#### 应用层

CMSIS没有提供直接类似FreeRTOS中临界段代码保护的API，用户可以自己根据CMSISI Core(即上面给出的底层API)封装，也可以使用FreeRTOS的API。

另外，CMSIS给出的是**调度器锁**（相当于锁住Pendsv）的API，防止其他任务切换，也可以用于不太严格的代码保护。（在下一节中调度器的挂起和恢复详解）

```c
//锁住调度器
int32_t osKernelLock (void);
//解锁调度器
uint32_t osKernelUnlock (void);
```

##### 封装参考

```c
#ifndef CRITICAL_H
#define CRITICAL_H

#include "cmsis_gcc.h"   

/* 配置项：参考 FreeRTOSConfig.h */
#ifndef configMAX_SYSCALL_INTERRUPT_PRIORITY
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 5
#endif

/* 获取 NVIC 实际优先级位数 */
#ifndef __NVIC_PRIO_BITS
#define __NVIC_PRIO_BITS 4
#endif

/* ------------------------------
   任务级临界区 (等价 taskENTER_CRITICAL)
   支持嵌套计数
--------------------------------*/
static inline void vTaskEnterCritical(void)
{
    static uint32_t ulCriticalNesting = 0;

    if(ulCriticalNesting == 0)
    {
        /* 第一次进入临界区，提升 BASEPRI */
        __set_BASEPRI(configMAX_SYSCALL_INTERRUPT_PRIORITY << (8 - __NVIC_PRIO_BITS));
        __DSB();
        __ISB();
    }

    ulCriticalNesting++;
}

static inline void vTaskExitCritical(void)
{
    extern uint32_t ulCriticalNesting;
    if(ulCriticalNesting > 0)
    {
        ulCriticalNesting--;

        /* 最外层临界区退出，恢复 BASEPRI */
        if(ulCriticalNesting == 0)
        {
            __set_BASEPRI(0);
            __DSB();
            __ISB();
        }
    }
}

/* ------------------------------
   ISR 上下文临界区 (等价 taskENTER_CRITICAL_FROM_ISR)
   返回原 BASEPRI 以便恢复
--------------------------------*/
static inline uint32_t ulEnterCriticalFromISR(void)
{
    uint32_t ulOriginalBASEPRI;

    /* 保存原 BASEPRI */
    ulOriginalBASEPRI = __get_BASEPRI();

    /* 提升 BASEPRI 屏蔽低优先级中断 */
    __set_BASEPRI(configMAX_SYSCALL_INTERRUPT_PRIORITY << (8 - __NVIC_PRIO_BITS));
    __DSB();
    __ISB();

    return ulOriginalBASEPRI;
}

static inline void vExitCriticalFromISR(uint32_t ulOriginalBASEPRI)
{
    /* 恢复 BASEPRI */
    __set_BASEPRI(ulOriginalBASEPRI);
    __DSB();
    __ISB();
}

#endif // CRITICAL_H
```

### API对比

| 功能                     | FreeRTOS API                                                 | CMSIS v2 API                                      | 推荐使用场景                                 |
| :----------------------- | :----------------------------------------------------------- | :------------------------------------------------ | :------------------------------------------- |
| **全局中断开关**（底层） | `portDISABLE_INTERRUPTS()` `portENABLE_INTERRUPTS()`         | `__disable_irq()` `__enable_irq()`                | FreeRTOS：在端口层使用 CMSIS：裸机或底层驱动 |
| **优先级屏蔽**           | `taskENTER_CRITICAL()` `taskEXIT_CRITICAL()`                 | `__set_BASEPRI()` `__get_BASEPRI()`               | **FreeRTOS推荐**：任务环境保护               |
| **ISR中断屏蔽**          | `taskENTER_CRITICAL_FROM_ISR()` `taskEXIT_CRITICAL_FROM_ISR()` | `__set_BASEPRI()` `__get_BASEPRI()`               | **FreeRTOS推荐**：ISR环境保护                |
| **故障屏蔽**             | 无直接API                                                    | `__set_FAULTMASK()` `__get_FAULTMASK()`           | CMSIS：故障处理程序                          |
| **中断使能控制**         | 无直接API                                                    | `NVIC_EnableIRQ()` `NVIC_DisableIRQ()`            | CMSIS：外设中断管理                          |
| **优先级配置**           | 通过`FreeRTOSConfig.h`                                       | `NVIC_SetPriority()` `NVIC_SetPriorityGrouping()` | CMSIS：中断优先级设置                        |