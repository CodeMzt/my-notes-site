[TOC]
# 基本概念

## 什么是调度器挂起

**调度器挂起**是指暂时停止操作系统的任务调度功能，但**不影响中断的正常执行**。

## 挂起调度器的效果：
-  **禁止**任务上下文切换
- **停止**时间片轮转
- **暂停**任务调度算法
- **不影响**中断执行
- **不影响**中断优先级
- **不屏蔽**硬件中断

## 典型使用场景：

1. **保护复杂的共享数据结构操作**
2. **执行需要原子性的多步操作**
3. **防止任务切换干扰关键代码段**
4. **与中断服务程序协同工作**

## 与临界区的区别

| 特性 | 调度器挂起 | 临界区 |
|------|------------|--------|
| **中断影响** | 中断正常执行 | 屏蔽部分中断 |
| **保护范围** | 仅任务切换 | 任务切换+部分中断 |
| **性能影响** | 较小 | 较大 |
| **使用场景** | 长时间操作 | 短时间操作 |

# FreeRTOS API 详解

## 函数原型

```c
/*=== 调度器控制 API ===*/

// 挂起所有任务调度（无返回值）
void vTaskSuspendAll(void);

// 恢复任务调度（返回是否需要进行上下文切换）
BaseType_t xTaskResumeAll(void);
```

## 功能特性

### 嵌套支持

FreeRTOS 的调度器挂起支持**完全嵌套**：

```c
// 嵌套示例
vTaskSuspendAll();    // 第1次挂起 - 调度器停止
vTaskSuspendAll();    // 第2次挂起 - 嵌套计数=2
vTaskSuspendAll();    // 第3次挂起 - 嵌套计数=3

xTaskResumeAll();     // 嵌套计数=2
xTaskResumeAll();     // 嵌套计数=1  
xTaskResumeAll();     // 嵌套计数=0，调度器真正恢复
```

### 返回值含义

`xTaskResumeAll()` 返回值：
- `pdTRUE`：在挂起期间有更高优先级任务就绪，需要立即上下文切换
- `pdFALSE`：没有需要立即切换的任务

## 使用示例

### 基本用法
```c
void ProtectExtendedOperation(void)
{
    // 挂起调度器
    vTaskSuspendAll();
    
    // 执行不受任务切换影响的扩展操作
    UpdateComplexDataStructures();
    ProcessMultipleSharedResources();
    GenerateConsistentSystemState();
    
    // 恢复调度器
    BaseType_t xYieldRequired = xTaskResumeAll();
    
    // 如果需要立即切换任务
    if(xYieldRequired != pdFALSE) {
        taskYIELD();
    }
}
```

## 函数内部分析

### 调度器挂起

```c
void vTaskSuspendAll( void )
{
	/* A critical section is not required as the variable is of type
	BaseType_t.  Please read Richard Barry's reply in the following link to a
	post in the FreeRTOS support forum before reporting this as a bug! -
	http://goo.gl/wu4acr */

	/* portSOFRWARE_BARRIER() is only implemented for emulated/simulated ports that
	do not otherwise exhibit real time behaviour. */
	portSOFTWARE_BARRIER();

	/* The scheduler is suspended if uxSchedulerSuspended is non-zero.  An increment
	is used to allow calls to vTaskSuspendAll() to nest. */
	++uxSchedulerSuspended;

	/* Enforces ordering for ports and optimised compilers that may otherwise place
	the above increment elsewhere. */
	portMEMORY_BARRIER();
}
```

可见，真正实现作用的只有 `++uxSchedulerSuspended;`这句，那么为什么？

我们要先看看**PendSv**调度的底层

#### Systick中断服务函数

提供心跳节拍，进行调度。

```c
void SysTick_Handler (void) {
  /* Clear overflow flag */
  SysTick->CTRL;

  if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED) {
    /* Call tick handler */
    xPortSysTickHandler();
  }
}
```

#### FreeRTOS响应函数

相应系统滴答计时器的中断服务函数

```c
void xPortSysTickHandler( void )
{
	/* The SysTick runs at the lowest interrupt priority, so when this interrupt
	executes all interrupts must be unmasked.  There is therefore no need to
	save and then restore the interrupt mask value as its value is already
	known. */
	portDISABLE_INTERRUPTS();
	{
		/* Increment the RTOS tick. */
		if( xTaskIncrementTick() != pdFALSE )
		{
			/* A context switch is required.  Context switching is performed in
			the PendSV interrupt.  Pend the PendSV interrupt. */
            //可以参见Cortex-M3手册，这个句子使芯片中断控制即状态寄存器ICSR(0xE000 ED04)中PENDSVSET位(28位)置1，开启调度。
			portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT;
		}
	}
	portENABLE_INTERRUPTS();
}
```

#### 任务调度器节拍函数

FreeRTOS 任务调度器内部用于增加时钟节拍计数并执行相关管理的函数

```c
BaseType_t xTaskIncrementTick( void )
{
    BaseType_t xSwitchRequired = pdFALSE;
    	...
        if( uxSchedulerSuspended == ( UBaseType_t ) pdFALSE )
	{	
            ...
        }
    else
	{
		++xPendedTicks;

		/* The tick hook gets called at regular intervals, even if the
		scheduler is locked. */
		#if ( configUSE_TICK_HOOK == 1 )
		{
			vApplicationTickHook();
		}
		#endif
	}
    	return xSwitchRequired;
}
```

并且有

```c
PRIVILEGED_DATA static volatile UBaseType_t uxSchedulerSuspended	= ( UBaseType_t ) pdFALSE;
```

说明`uxSchedulerSuspended`本来为`pdFALSE`，我们++后它不是了，因此之后的调度无法进行。

| 特性                 | 描述                                                         |
| :------------------- | :----------------------------------------------------------- |
| **变量类型**         | 计数器（可嵌套）                                             |
| **有效值**           | `0`：调度器活跃； `>0`：调度器挂起                           |
| **相关函数**         | `vTaskSuspendAll()`, `xTaskResumeAll()`                      |
| **主要目的**         | 实现内核数据操作的原子性，保护关键段                         |
| **对节拍中断的影响** | 挂起时，节拍正常计数，任务超时被记录但切换被延迟，`xTaskIncrementTick` 返回 `pdFALSE` |

# CMSIS v2 API 详解

## 函数原型

```c
/*=== CMSIS-RTOS v2 调度器控制 API ===*/

// 挂起任务调度器（返回执行状态）
osStatus_t osKernelLock(void);

// 恢复任务调度器（返回执行状态）  
osStatus_t osKernelUnlock(void);
```

### 状态返回值

#### osKernelLock() 返回值：
- `osOK`：成功挂起调度器
- `osError`：调度器未启动或其他错误
- `osErrorISR`：在中断上下文中调用（错误用法）

#### osKernelUnlock() 返回值：
- `osOK`：成功恢复调度器
- `osError`：调度器未挂起或其他错误

## 功能特性

### 嵌套支持
CMSIS v2 同样支持完整的嵌套机制：

```c
osKernelLock();     // 锁定计数 = 1
osKernelLock();     // 锁定计数 = 2
osKernelLock();     // 锁定计数 = 3

osKernelUnlock();   // 锁定计数 = 2
osKernelUnlock();   // 锁定计数 = 1
osKernelUnlock();   // 锁定计数 = 0，调度器恢复
```

## 使用示例

### 基本用法
```c
void CMSIS_SchedulerControl(void)
{
    osStatus_t status;
    
    // 挂起调度器
    status = osKernelLock();
    if (status == osOK) {
        
        // 执行受保护的操作
        AccessSharedResources();
        UpdateGlobalData();
        PerformAtomicOperations();
        
        // 恢复调度器
        osStatus_t unlock_status = osKernelUnlock();
        if (unlock_status != osOK) {
            // 处理恢复失败
            HandleKernelError(unlock_status);
        }
    } else {
        // 处理挂起失败
        HandleKernelError(status);
    }
}
```

### 嵌套使用
```c
void NestedKernelLockExample(void)
{
    osStatus_t status;
    
    // 第一层锁定
    status = osKernelLock();
    if (status != osOK) return;
    
    OperationA();
    
    // 第二层锁定
    status = osKernelLock();
    if (status != osOK) {
        osKernelUnlock();  // 恢复第一层
        return;
    }
    
    OperationB();
    osKernelUnlock();  // 恢复第二层
    
    OperationC();
    osKernelUnlock();  // 恢复第一层
}
```

# 对比分析

## API 对比表

| 特性 | FreeRTOS | CMSIS v2 |
|------|----------|----------|
| **挂起函数** | `vTaskSuspendAll()` | `osKernelLock()` |
| **恢复函数** | `xTaskResumeAll()` | `osKernelUnlock()` |
| **返回值** | `BaseType_t`（是否需要切换） | `osStatus_t`（执行状态） |
| **嵌套支持** | ✅ 完全支持 | ✅ 完全支持 |
| **中断安全** | ❌ 不能在ISR中使用 | ❌ 不能在ISR中使用 |
| **错误处理** | 简单 | 详细的错误码 |

## 适用场景对比

### FreeRTOS 优势场景：
- **需要知道恢复后是否需要任务切换**
- **对性能要求极高的系统**
- **已经深度使用FreeRTOS的项目**

### CMSIS v2 优势场景：
- **需要跨RTOS移植性的项目**
- **需要详细错误处理的系统**
- **新项目或要求标准化接口的项目**

## 性能考虑

| 操作 | FreeRTOS | CMSIS v2 |
|------|----------|----------|
| **挂起开销** | 很低（主要是计数操作） | 较低（包含状态检查） |
| **恢复开销** | 低（包含就绪任务检查） | 低（状态验证） |
| **内存占用** | 很小（一个计数器） | 较小（状态管理） |

# 实践应用

### 选择指南

#### 使用调度器挂起的场景：
```c
// ✅ 适合使用调度器挂起的情况：

// 1. 多个相关的共享资源操作
vTaskSuspendAll();  // 或 osKernelLock()
UpdateUserAccount();
UpdateTransactionLog();
UpdateSystemStatistics();
xTaskResumeAll();   // 或 osKernelUnlock()

// 2. 复杂数据结构的维护
vTaskSuspendAll();
RebalanceTreeStructure();
UpdateAllRelatedNodes();
VerifyDataConsistency();
xTaskResumeAll();

// 3. 与ISR协作的扩展操作
vTaskSuspendAll();
SetupHardwareForBatchProcessing();
// ISR可以在此期间收集数据
WaitForDataCollectionComplete();
ProcessCollectedData();
xTaskResumeAll();
```

#### 不适合使用的场景：
```c
// ❌ 避免使用调度器挂起的情况：

// 1. 非常短的操作（使用临界区更好）
taskENTER_CRITICAL();
single_variable_update++;
taskEXIT_CRITICAL();

// 2. 需要中断保护的操作（使用临界区）
taskENTER_CRITICAL();
hardware_register_access();
taskEXIT_CRITICAL();

// 3. 可能阻塞的操作
vTaskSuspendAll();
wait_for_external_event();  // ❌ 危险！
xTaskResumeAll();
```

### 最佳实践

#### 1. 保持挂起时间最短
```c
// ✅ 好的做法
vTaskSuspendAll();
// 只包含必要的操作
essential_operations_only();
xTaskResumeAll();

// 将非关键操作移到外面
non_critical_operations();
```

#### 2. 避免在挂起期间调用阻塞函数
```c
// ❌ 危险做法
vTaskSuspendAll();
xQueueSend( xQueue, &data, portMAX_DELAY );  // 可能永远阻塞！
xTaskResumeAll();

// ✅ 安全做法
vTaskSuspendAll();
BaseType_t xResult = xQueueSend( xQueue, &data, 0 );  // 不阻塞
xTaskResumeAll();

if(xResult != pdPASS) {
    // 处理队列已满的情况
}
```

#### 3. 与中断的正确协作
```c
// 任务中的代码
vTaskSuspendAll();
// 设置硬件，启动操作
SetupDMA_Transfer();
// 此时ISR仍然可以运行并处理DMA完成
xTaskResumeAll();

// ISR中的代码（不能调用调度器控制函数）
void DMA_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 处理DMA完成，但不会导致任务切换
    if(xQueueSendFromISR(xDataQueue, &data, &xHigherPriorityTaskWoken) == pdPASS) {
        // 成功发送，但xHigherPriorityTaskWoken可能被忽略
        // 直到调度器恢复后才会实际切换任务
    }
}
```

### 调试和监控

#### FreeRTOS 调试技巧
```c
// 检查调度器状态
#if ( configUSE_TRACE_FACILITY == 1 )
void CheckSchedulerState(void)
{
    UBaseType_t uxSchedulerState = xTaskGetSchedulerState();
    
    if(uxSchedulerState == taskSCHEDULER_SUSPENDED) {
        printf("调度器已挂起\n");
    } else if(uxSchedulerState == taskSCHEDULER_RUNNING) {
        printf("调度器运行中\n");
    } else {
        printf("调度器未启动\n");
    }
}
#endif
```

#### CMSIS v2 调试技巧
```c
// 监控内核状态
void MonitorKernelState(void)
{
    osKernelState_t state = osKernelGetState();
    
    switch(state) {
        case osKernelInactive:
            printf("内核未初始化\n");
            break;
        case osKernelReady:
            printf("内核就绪\n");
            break;
        case osKernelRunning:
            printf("内核运行中\n");
            break;
        case osKernelLocked:
            printf("内核已锁定\n");
            break;
        case osKernelSuspended:
            printf("内核已挂起\n");
            break;
        case osKernelError:
            printf("内核错误\n");
            break;
    }
}
```

# 总结

**关键要点：**

1. **调度器挂起只影响任务切换，不影响中断**
2. **两个系统都支持完整的嵌套机制**
3. **FreeRTOS 提供切换需求信息，CMSIS v2 提供错误状态**
4. **适合保护扩展操作，但不适合短时间保护**
5. **必须确保在所有代码路径上都恢复调度器**

# 注意

​	我发现，FreeRTOS的调度器恢复API会处理是否需要任务切换（即在锁死期间如果有高优先级的任务就绪了，退出锁死时需要马上切换任务，而不是等到下一个时间片由系统去切换），而CMSIS没有这个功能，我们关注解锁这个函数：
## 分析

`osKernelUnlock` 确实内部调用了 `xTaskResumeAll()`，但它的**返回值语义完全不同**：

```c
int32_t osKernelUnlock (void) {
  int32_t lock;

  // ... 简化代码 ...
  if (xTaskResumeAll() != pdTRUE) {
    if (xTaskGetSchedulerState() == taskSCHEDULER_SUSPENDED) {
      lock = (int32_t)osError;
    }
  }
  // ...
  return (lock);
}
```

## 关键差异：返回值含义

### `xTaskResumeAll()` 的返回值：
- `pdTRUE` = 需要上下文切换
- `pdFALSE` = 不需要上下文切换

### `osKernelUnlock()` 的返回值：
- `> 0` = 剩余的锁计数（锁状态）
- `0` = 调度器已完全解锁
- `< 0` = 错误状态（`osError`, `osErrorISR`）

## 为什么设计不同？

### 1. **抽象层次不同**

`osKernelUnlock` 是 **CMSIS-RTOS API**，关注的是**锁状态**：
```c
// CMSIS-RTOS 的使用模式
int32_t lock_count = osKernelUnlock();
// 用户关心的是：锁是否完全解开了？还剩几层锁？
```

`xTaskResumeAll` 是 **FreeRTOS 内核API**，关注的是**调度决策**：
```c
// FreeRTOS 内核的使用模式  
if (xTaskResumeAll() == pdTRUE) {
    taskYIELD(); // 立即执行调度
}
```

### 2. **错误处理机制**

`osKernelUnlock` 有完整的错误检查：
- 检查是否在中断中调用（返回 `osErrorISR`）
- 检查调度器状态（`taskSCHEDULER_NOT_STARTED` 返回 `osError`）
- 检查恢复操作是否成功

而 `xTaskResumeAll` 假设调用环境正确，专注于调度逻辑。

### 3. **锁计数管理**

`osKernelUnlock` 返回的是**剩余的锁计数**，这反映了 CMSIS-RTOS 对嵌套锁的支持：

```c
osKernelLock();   // 锁计数 = 1
osKernelLock();   // 锁计数 = 2  
int32_t count = osKernelUnlock(); // count = 1, 调度器仍被锁定
```

## 调度切换的处理

那么，如果 `xTaskResumeAll()` 返回 `pdTRUE`（需要切换），在 `osKernelUnlock` 中这个信息去哪了？

**答案：这个信息被丢弃了！**

```c
// 在 osKernelUnlock 中：
if (xTaskResumeAll() != pdTRUE) {
  // 只处理 FALSE 情况（恢复失败）
  // 如果返回 TRUE（需要切换），这个信息被忽略
}
```

## 这种设计的合理性

### 1. **API 简洁性**
CMSIS-RTOS 选择提供简单的锁状态管理，而不是暴露底层的调度决策。

### 2. **延迟调度可接受**
在大多数应用场景中，稍微延迟的调度是可以接受的。系统会在下一个时间片或调度点自然处理切换。

### 3. **使用场景不同**
```c
// 需要精确控制调度的场景 - 用 FreeRTOS 原生 API
vTaskSuspendAll();
// 精确的临界区操作
if (xTaskResumeAll() == pdTRUE) {
    portYIELD_WITHIN_API(); // 立即切换
}

// 一般的临界区保护 - 用 CMSIS-RTOS API  
osKernelLock();
// 一般的共享资源访问
osKernelUnlock(); // 不关心立即切换
```

这体现了不同抽象层次的设计取舍：CMSIS-RTOS 追求**易用性和可移植性**，而 FreeRTOS 内核提供**精确控制和最高性能**。