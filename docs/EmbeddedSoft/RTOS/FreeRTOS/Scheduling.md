[TOC]
# 启动任务调度器

## CMSIS级别操作

```c
osStatus_t osKernelStart (void) {
  osStatus_t stat;

  if (IS_IRQ()) {
    stat = osErrorISR;
  }
  else {
    if (KernelState == osKernelReady) {
      /* Ensure SVC priority is at the reset value */
      SVC_Setup();
      /* Change state to enable IRQ masking check */
      KernelState = osKernelRunning;
      /* Start the kernel scheduler */
      vTaskStartScheduler();
      stat = osOK;
    } else {
      stat = osError;
    }
  }

  return (stat);
}
```

### `SVC_Setup()`

这一句 `SVC_Setup();` 在 CMSIS-RTOS2 的 `osKernelStart()` 函数中，主要目的是**确保 SVC（Supervisor Call）异常的优先级被设置为复位后的默认值**。
关于**异常**可看[Interrupt_Mgmt](Interrupt_Mgmt.md)

#### 详细解释：

##### 1. SVC 异常的作用

- SVC 是 ARM Cortex-M 处理器的一个系统异常
- RTOS 使用 SVC 异常来实现从用户模式（线程模式）到特权模式（处理器模式）的安全切换
- 系统调用（如创建线程、信号量操作等）通常通过 SVC 指令触发

##### 2. 为什么要设置 SVC 优先级

- 在系统启动过程中，某些初始化代码或第三方库可能会修改 SVC 的优先级
- 如果 SVC 优先级设置不当，可能导致：
  - 系统调用无法正确执行
  - 任务调度出现问题
  - 系统稳定性降低

##### 3. `SVC_Setup()` 的具体工作

```c
static void SVC_Setup (void) {
  #if   (defined(__ARM_ARCH_7M__) && (__ARM_ARCH_7M__ != 0)) || \
        (defined(__ARM_ARCH_7EM__) && (__ARM_ARCH_7EM__ != 0))
  SCB->SHCSR |= SCB_SHCSR_SVCALLUSED_Msk;  // 启用 SVC 异常
  NVIC_SetPriority(SVCall_IRQn, 0xFE);     // 设置较低的优先级
  #endif
}
```



##### 4. 在 `osKernelStart()` 中的意义

- 确保内核启动前 SVC 异常处于已知的、正确的状态
- 为后续的系统调用和任务调度提供可靠的基础
- 这是 RTOS 启动过程中的重要安全措施

## FreeRTOS级别操作

### `vTaskStartScheduler()`

```c
void vTaskStartScheduler( void )
{
    /* Add the idle task at the lowest priority. */
    //1.创建空闲任务
    xTaskCreate() or xTaskCreateStatic()
        
    //2.创建软件定时器任务（如果使能）
    xTimerCreateTimerTask()
    
    //3.关中断，防止调度器开启之前或之中受中断干扰
    portDISABLE_INTERRUPTS();
    
    xNextTaskUnblockTime = portMAX_DELAY; //设置第一个任务的阻塞超时时间为很大0xffffffffUL
	xSchedulerRunning = pdTRUE; //标记任务调度器开始运行
	xTickCount = ( TickType_t ) configINITIAL_TICK_COUNT; //初始化心跳计数器为0
    
    portCONFIGURE_TIMER_FOR_RUN_TIME_STATS();//统计任务运行时间的实现接口（用户实现）
    
    traceTASK_SWITCHED_IN()//调试接口，需要实现
```

### `xPortStartScheduler()`

`xPortStartScheduler()` 是 FreeRTOS 调度器的核心启动函数，负责初始化硬件资源并启动多任务调度环境。

#### 函数概述

`xPortStartScheduler()` 位于 FreeRTOS 的移植层（通常是 `port.c` 文件），主要职责包括：

- 配置系统关键硬件（如 SysTick 定时器）
- 设置异常优先级
- 启动第一个任务
- 永不返回（除非发生严重错误）

#### 代码分析

##### 1. 异常优先级配置

```c
BaseType_t xPortStartScheduler( void )
{
    /* 配置 PendSV 和 SysTick 异常的优先级 */
    portNVIC_SYSPRI2_REG |= portNVIC_PENDSV_PRI;
    portNVIC_SYSPRI2_REG |= portNVIC_SYSTICK_PRI;
```

**关键设计要点**：

- PendSV 优先级设置为最低，确保高优先级中断能够立即响应
- 这种设计避免了任务切换阻塞时间敏感的中断处理

##### 2. 系统定时器初始化

```c
    /* 启动 SysTick 定时器 - 提供任务调度的时间基准 */
    vPortSetupTimerInterrupt();
```

SysTick 定时器的作用：
- 产生固定的时间节拍（tick）
- 驱动时间片轮转调度
- 管理阻塞任务的超时机制

##### 3. 调度器状态初始化

```c
    /* 初始化调度器关键变量 */
    xNextTaskUnblockTime = portMAX_DELAY;
    xSchedulerRunning = pdTRUE;
    xTickCount = 0;
```

##### 4. 启动第一个任务

```c
    /* 启动第一个任务 */
    if( xPortStartFirstTask() != pdFALSE )
    {
        /* 如果执行到这里，说明任务启动失败 */
        return pdFALSE;
    }
    
    /* 正常情况下不会到达这里 */
    return pdFALSE;
}
```

#### 启动第一个任务的核心机制

`xPortStartFirstTask()` 通常用汇编语言实现，主要步骤包括：

##### 1. 堆栈指针初始化

```assembly
xPortStartFirstTask:
    /* 从向量表初始化主堆栈指针 */
    ldr r0, =0xE000ED08    /* VTOR 寄存器地址 */
    ldr r0, [r0]
    ldr r0, [r0]           /* 获取初始 MSP 值 */
    msr msp, r0            /* 设置主堆栈指针 */
```

##### 2. 中断使能

```assembly
    /* 使能全局中断 */
    cpsie i                /* 使能 IRQ 中断 */
    cpsie f                /* 使能 Fault 中断 */
    dsb
    isb
```

##### 3. 触发 SVC 异常启动任务

```assembly
    /* 通过 SVC 异常启动第一个任务 */
    svc 0                  /* 触发 SVC 异常 */
    
    /* SVC 异常处理程序会配置任务环境并开始执行 */
```

#### SVC 异常处理程序的关键操作

在 SVC 异常处理程序中完成以下关键操作：

##### 1. 任务上下文恢复

```c
void vPortSVCHandler( void )
{
    /* 从当前任务的 TCB 中恢复堆栈指针 */
    pxCurrentTCB = 获取最高优先级任务的 TCB;
    __asm volatile (
        "ldr r3, [%0]          \n" /* 从 TCB 获取堆栈指针 */
        "ldmdb r3!, {r0-r2}    \n" /* 恢复部分寄存器 */
        "msr control, r0       \n" /* 设置控制寄存器 */
        "msr psp, r3           \n" /* 设置进程堆栈指针 */
        "isb                   \n"
        :: "r" (&pxCurrentTCB)
    );
}
```

##### 2. 切换到任务模式

```c
    /* 使用进程堆栈执行任务 */
    __asm volatile (
        "mov r0, #2            \n" /* 切换到线程模式并使用 PSP */
        "msr control, r0       \n"
        "isb                   \n"
        "bx lr                 \n" /* 返回到任务代码 */
    );
```

#### 设计原理分析

##### 1. 为什么使用 SVC 异常启动任务？

- **权限切换**：从 Handler 模式（特权级）切换到 Thread 模式（可能为非特权级）
- **环境隔离**：确保任务在受控的环境中开始执行
- **堆栈分离**：实现主堆栈（MSP）和进程堆栈（PSP）的分离

##### 2. 优先级配置的重要性

- **SysTick**：需要适当的优先级来保证时间基准的准确性
- **PendSV**：最低优先级确保不会延迟高优先级中断的处理
- **SVC**：用于系统调用，需要合理的优先级设置

##### 3. 状态机转换

调度器启动过程的状态转换：
1. **初始化状态**：配置硬件，设置优先级
2. **准备状态**：初始化变量，启动定时器
3. **启动状态**：通过 SVC 异常切换到第一个任务
4. **运行状态**：多任务环境正式运行

#### 错误处理机制

##### 启动失败的可能原因

- 堆栈指针初始化失败
- 向量表配置错误
- 优先级配置冲突
- 内存分配问题

##### 返回值语义

- **pdTRUE**：启动成功（实际上不会返回）
- **pdFALSE**：启动失败，需要错误处理

# 任务切换

任务切换的**本质**：**CPU寄存器的切换**

### 基本概念
任务切换是多任务操作系统的核心机制，指 CPU 从一个正在运行的任务转移到另一个任务的过程。在单核处理器系统中，多个任务通过快速切换创造"同时运行"的假象。

### 类比理解
想象一名厨师同时处理多道菜品：
- 每道菜就是一个任务
- 厨师在不同菜品间快速切换注意力
- 每次切换时需要记住当前菜品的进度
- 切换到另一道菜时需要回忆该菜品的上次状态

## 上下文切换的深入理解

### 什么是上下文
上下文是指任务在某个时间点的完整执行状态，包括：

**硬件上下文：**
- 所有寄存器值（R0-R15）
- 程序状态寄存器（xPSR）
- 堆栈指针（SP）
- 程序计数器（PC）

**软件上下文：**
- 任务控制块（TCB）中的状态信息
- 堆栈中的局部变量和返回地址
- 任务特有的配置和数据

### 上下文切换的过程
```c
// 伪代码表示上下文切换流程
void context_switch(Task* current, Task* next) {
    // 1. 保存当前任务上下文
    save_registers(current->stack_pointer);
    save_processor_state(current->tcb);
    
    // 2. 更新调度器状态
    scheduler->current_task = next;
    
    // 3. 恢复新任务上下文  
    restore_processor_state(next->tcb);
    restore_registers(next->stack_pointer);
    
    // 4. 跳转到新任务
    jump_to_task(next->program_counter);
}
```

## FreeRTOS 任务切换的触发条件

### 主动触发方式

**任务主动让出 CPU `portYIELD()/taskYIELD()`：**

通过挂起PendSV启用PendSv异常，如何挂起见[KernelPend](KernelPend.md)

```c
void vTaskA( void *pvParameters )
{
    for( ;; )
    {
        // 执行一些工作
        perform_work();
        
        // 主动让出 CPU 给其他任务
        taskYIELD();
    }
}
```

**等待资源时自动切换：**
```c
void vTaskB( void *pvParameters )
{
    for( ;; )
    {
        // 等待信号量，期间会自动切换任务
        xSemaphoreTake( xBinarySemaphore, portMAX_DELAY );
        
        // 获取信号量后继续执行
        process_data();
    }
}
```

### 被动触发方式

**时间片到期：**
```c
// 在 SysTick 中断服务程序中
void xPortSysTickHandler( void )
{
    // 更新时间计数
    if( xTaskIncrementTick() != pdFALSE )
    {
        // 触发任务切换
        portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT;
    }
}
```

**中断服务程序中唤醒高优先级任务：**
```c
void vAnInterruptHandler( void )
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 释放信号量，可能唤醒高优先级任务
    xSemaphoreGiveFromISR( xSemaphore, &xHigherPriorityTaskWoken );
    
    // 如果需要立即切换
    portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
}
```

## FreeRTOS 任务切换的硬件机制

### ARM Cortex-M 异常系统

FreeRTOS 充分利用 ARM Cortex-M 的异常机制来实现高效任务切换：

**SysTick 异常：**
- 用途：系统时钟节拍，提供时间基准
- 优先级：配置为较低优先级
- 功能：驱动时间片轮转和任务超时管理

**PendSV 异常：**

- 用途：可挂起的系统服务，执行实际上下文切换
- 优先级：配置为最低优先级
- 特点：可延迟执行，不阻塞高优先级中断

**SVC 异常：**
- 用途：**系统**调用接口
- 功能：启动调度器和执行**特权**操作

### 优先级配置策略
```c
// FreeRTOSConfig.h 中的典型配置
#define configKERNEL_INTERRUPT_PRIORITY    255
#define configMAX_SYSCALL_INTERRUPT_PRIORITY  191

// 实际优先级设置
#define portNVIC_PENDSV_PRI          ( ( ( uint32_t ) configKERNEL_INTERRUPT_PRIORITY ) << 16UL )
#define portNVIC_SYSTICK_PRI         ( ( ( uint32_t ) configKERNEL_INTERRUPT_PRIORITY ) << 24UL )
```

## 任务切换的详细执行流程

### 完整的切换序列

**阶段一：触发切换**
```c
// 从任务中触发切换
taskYIELD();
    ↓
// 设置 PendSV 挂起位
portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT;
    ↓
// CPU 在适当时候进入 PendSV 异常
```

**阶段二：保存当前任务上下文**
```assembly
vPortPendSVHandler:
    /* 保存当前任务状态 */
    mrs r0, psp                 // 获取当前任务的堆栈指针
    isb                         // 指令同步屏障
    
    // 将寄存器 r4-r11 保存到任务堆栈（手动压栈）
    stmdb r0!, {r4-r11}
    
    // 更新任务控制块中的堆栈指针
    ldr r2, =pxCurrentTCB
    ldr r1, [r2]
    str r0, [r1]
```

**阶段三：选择下一个任务**
```c
// 调用调度器选择新任务
vTaskSwitchContext();
    ↓
// 调度器决策过程
void vTaskSwitchContext( void )
{
    // 检查调度器是否挂起
    if( uxSchedulerSuspended != ( UBaseType_t ) pdFALSE )
    {
        xYieldPending = pdTRUE;
        return;
    }
    
    // 寻找最高优先级的就绪任务
    #if ( configUSE_PORT_OPTIMISED_TASK_SELECTION == 1 )
        // 使用位图算法快速查找
        uxTopReadyPriority = portGET_HIGHEST_PRIORITY();
    #else
        // 遍历就绪列表查找
        listGET_OWNER_OF_NEXT_ENTRY( pxCurrentTCB, 
                                   &( pxReadyTasksLists[ uxTopReadyPriority ] ) );
    #endif
}
```

**阶段四：恢复新任务上下文**
```assembly
    /* 恢复新任务状态 */
    ldr r1, =pxCurrentTCB      // 获取新任务的 TCB
    ldr r0, [r1]
    ldr r0, [r0]               // 获取新任务的堆栈指针
    
    // 从堆栈恢复寄存器 r4-r11
    ldmia r0!, {r4-r11}
    
    // 更新进程堆栈指针
    msr psp, r0
    isb
    
    // 返回到新任务继续执行
    bx r14
```

## 任务控制块（TCB）的关键作用

### TCB 数据结构
```c
typedef struct tskTaskControlBlock
{
    // 堆栈管理
    volatile StackType_t *pxTopOfStack;    // 当前堆栈顶
    StackType_t *pxStack;                  // 堆栈起始地址
    
    // 任务状态管理
    ListItem_t xStateListItem;             // 状态列表项
    UBaseType_t uxPriority;                // 任务优先级
    StackType_t *pxEndOfStack;             // 堆栈结束地址
    
    // 任务标识
    char pcTaskName[ configMAX_TASK_NAME_LEN ];
    
    // 调试和跟踪信息
    #if ( configUSE_TRACE_FACILITY == 1 )
        UBaseType_t uxTCBNumber;
    #endif
        
    // 互斥量继承相关
    #if ( configUSE_MUTEXES == 1 )
        UBaseType_t uxBasePriority;
        UBaseType_t uxMutexesHeld;
    #endif
} tskTCB;
```

### 堆栈布局设计
```
任务堆栈在上下文保存后的布局：
高地址 -> | 异常自动保存的寄存器(自动压栈，自动出栈) |
         | R0-R3, R12, LR, PC, xPSR |
         |---------------------------|
         | 手动保存的寄存器 R4-R11 (手动压栈，手动出栈)  | <- PSP 指向这里
         |---------------------------|
         | 任务局部变量和调用栈      |
低地址 -> | 堆栈起始位置            |
```

## 时间片轮转调度原理

### 同优先级任务调度
```c
// 在 SysTick 中断中处理时间片
BaseType_t xTaskIncrementTick( void )
{
    TickType_t xSwitchRequired = pdFALSE;
    
    if( xSchedulerRunning != pdFALSE )
    {
        // 更新系统节拍计数
        const TickType_t xConstTickCount = xTickCount + 1;
        xTickCount = xConstTickCount;
        
        // 检查是否有任务超时
        if( xConstTickCount == 0 )
        {
            taskSWITCH_DELAYED_LISTS();
        }
        
        // 时间片轮转决策
        #if ( configUSE_PREEMPTION == 1 ) && ( configUSE_TIME_SLICING == 1 )
        {
            // 如果当前优先级有多个就绪任务，触发切换
            if( listCURRENT_LIST_LENGTH( 
                &( pxReadyTasksLists[ pxCurrentTCB->uxPriority ] ) ) > ( UBaseType_t ) 1 )
            {
                xSwitchRequired = pdTRUE;
            }
        }
        #endif
    }
    
    return xSwitchRequired;
}
```

## 性能优化技术

### 快速任务选择算法

**位图调度算法：**
```c
#if configUSE_PORT_OPTIMISED_TASK_SELECTION == 1

// 使用前导零计数指令快速找到最高优先级
#define portGET_HIGHEST_PRIORITY( uxTopPriority, uxReadyPriorities ) \
    __asm volatile( "clz %0, %1" : "=r" ( uxTopPriority ) : "r" ( uxReadyPriorities ) )

#endif
```

**惰性堆栈保存：**
- 只保存被调用者保存的寄存器（R4-R11）
- 调用者保存的寄存器（R0-R3, R12）由 C-ABI 保证
- 硬件自动保存异常帧（R0-R3, R12, LR, PC, PSR）

### 中断延迟优化

**PendSV 的低优先级设计：**
```c
// PendSV 设置为最低优先级，确保：
// 1. 高优先级中断可以立即响应
// 2. 多个中断可以合并处理
// 3. 减少不必要的上下文切换

#define portPendSVHandler_PRIORITY ( 255UL << 16UL )
```

## 实际应用场景分析

### 场景一：高优先级任务抢占
```c
void vHighPriorityTask( void *pvParameters )
{
    for( ;; )
    {
        // 等待事件
        xQueueReceive( xHighPriorityQueue, ... );
        
        // 立即抢占当前运行的低优先级任务
        process_critical_work();
    }
}

void vLowPriorityTask( void *pvParameters )
{
    for( ;; )
    {
        // 执行非关键工作
        background_processing();
        
        // 可能在任何时刻被高优先级任务抢占
        taskYIELD();
    }
}
```

### 场景二：资源共享与同步
```c
void vProducerTask( void *pvParameters )
{
    for( ;; )
    {
        // 生产数据
        generate_data();
        
        // 发送数据到队列，可能唤醒消费者任务
        xQueueSend( xDataQueue, &data, portMAX_DELAY );
        
        // 如果消费者优先级更高，会发生任务切换
    }
}

void vConsumerTask( void *pvParameters )
{
    for( ;; )
    {
        // 等待数据，如果没有数据会阻塞
        xQueueReceive( xDataQueue, &data, portMAX_DELAY );
        
        // 被生产者唤醒后继续执行
        process_data( data );
    }
}
```

## 调试与性能分析

### 上下文切换开销测量
```c
// 测量切换时间的简单方法
uint32_t measure_switch_time( void )
{
    uint32_t start_time, end_time;
    
    // 获取开始时间
    start_time = DWT->CYCCNT;
    
    // 触发任务切换
    taskYIELD();
    
    // 获取结束时间
    end_time = DWT->CYCCNT;
    
    return end_time - start_time;
}
```

### 常见问题与解决方案

**问题一：过多的上下文切换**
- 症状：CPU 大部分时间在切换任务而非执行任务
- 解决方案：调整时间片大小，合并小任务

**问题二：优先级反转**
- 症状：高优先级任务被低优先级任务阻塞
- 解决方案：使用优先级继承协议或优先级天花板

**问题三：堆栈溢出**
- 症状：任务崩溃或系统不稳定
- 解决方案：增加堆栈大小，使用堆栈检查功能

# 其他API函数
### FreeRTOS 

这些函数以 `vTask`、`xTask` 等为前缀，是 FreeRTOS 内核的直接接口。

| 分类           | 函数名                          | 功能描述                                         | 参数说明                                         | 返回值/注意事项                                              |
| :------------- | :------------------------------ | :----------------------------------------------- | :----------------------------------------------- | :----------------------------------------------------------- |
|                | `taskYIELD()`                   | 主动请求任务切换（强制调度）。                   | 无                                               | 是一个宏，通常触发 PendSV 异常。                             |
| **优先级管理** | `vTaskPrioritySet()`            | 设置任务的优先级。                               | `xTask`: 任务句柄<br>`uxNewPriority`: 新的优先级 | 优先级必须在 `0` 到 `configMAX_PRIORITIES-1` 范围内。        |
|                | `uxTaskPriorityGet()`           | 获取任务的当前优先级。                           | `xTask`: 任务句柄                                | 返回任务的当前优先级。                                       |
| **状态查询**   | `eTaskGetState()`               | 获取任务的状态（运行、就绪、阻塞、挂起、删除）。 | `xTask`: 任务句柄                                | 返回一个 `eTaskState` 枚举值。                               |
|                | `uxTaskGetStackHighWaterMark()` | 获取任务堆栈的历史最小剩余空间（高水位线）。     | `xTask`: 任务句柄                                | 返回值越小，说明堆栈使用率越高。0 表示堆栈已溢出。用于评估堆栈大小是否合理。 |
| **其他**       | `pcTaskGetName()`               | 获取任务的名称字符串。                           | `xTaskToQuery`: 任务句柄                         | 返回任务名称字符串的指针。                                   |
|                | `xTaskGetTickCount()`           | 获取系统节拍计数器自启动以来的值。               | 无                                               | 在任务中使用。注意节拍计数器溢出。                           |
|                | `xTaskGetTickCountFromISR()`    | 在中断服务程序中获取系统节拍计数器。             | 无                                               | 在 ISR 中使用。                                              |

---

## CMSIS-RTOS v2 

这些函数以 `osThread` 为前缀，是 FreeRTOS 原生 API 的封装，提供了标准化的接口。

| 分类             | 函数名                       | 功能描述                                      | 参数说明                                       | 返回值/注意事项                                              |
| :--------------- | :--------------------------- | :-------------------------------------------- | :--------------------------------------------- | :----------------------------------------------------------- |
|                  | `osThreadGetId()`            | 获取当前正在运行的线程的 ID。                 | 无                                             | 返回当前线程的 ID。                                          |
|                  | `osThreadGetName()`          | 获取指定线程的名称字符串。                    | `thread_id`: 线程 ID                           | 返回线程名称字符串的指针。                                   |
| **任务控制**     | `osDelay()`                  | 将当前线程延迟（阻塞）指定的时间。            | `ticks`: 延迟的时间节拍数                      | 相当于 FreeRTOS 的 `vTaskDelay`。                            |
|                  | `osDelayUntil()`             | 精确的周期性延迟。                            | `ticks`: 下一次唤醒的绝对节拍时间              | 相当于 FreeRTOS 的 `vTaskDelayUntil`。                       |
|                  | `osThreadYield()`            | 将 CPU 控制权交给另一个就绪态的同优先级线程。 | 无                                             | 相当于 FreeRTOS 的 `taskYIELD()`。                           |
| **状态与优先级** | `osThreadGetState()`         | 获取当前线程的状态。                          | `thread_id`: 线程 ID                           | 返回一个 `osThreadState_t` 枚举值（就绪、运行、阻塞、终止等）。 |
|                  | `osThreadSetPriority()`      | 设置指定线程的优先级。                        | `thread_id`: 线程 ID<br>`priority`: 新的优先级 | 优先级在 `osPriority_t` 枚举中定义。                         |
|                  | `osThreadGetPriority()`      | 获取指定线程的当前优先级。                    | `thread_id`: 线程 ID                           | 返回线程的当前优先级。                                       |
| **系统信息**     | `osThreadGetStackSpace()`    | （可选）获取线程的剩余堆栈空间。              | `thread_id`: 线程 ID                           | 返回值依赖于具体实现，可能返回字节数或字数的剩余空间。       |
|                  | `osKernelGetTickCount()`     | 获取内核节拍计数器。                          | 无                                             | 相当于 FreeRTOS 的 `xTaskGetTickCount`，可在任务和中断中使用。 |
|                  | `osKernelGetSysTimerCount()` | 获取系统计时器的精确计数值。                  | 无                                             | 用于高精度时间测量。                                         |
