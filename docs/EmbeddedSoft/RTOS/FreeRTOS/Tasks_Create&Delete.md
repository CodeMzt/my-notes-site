[TOC]

# 1. 原生API 

- `xTaskCreate()` 动态方式创建，FreeRTOS给我们分配
- `xTaskCreateStatic()` 静态方式创建，我们自己分配内存
- `xTaskDelete()` 删除任务
- `vTaskStartScheduler()` 启动任务调度

## **`xTaskCreate()`**

### 说明
动态创建内存

```c
BaseType_t xTaskCreate( 
    TaskFunction_t 					pxTaskCode,		 /*指向任务函数的指针*/
    const char * const 				pcName,    		 /*任务名字，大小配置过:configMAX_TASK_NAME_LEN*/
    const configSTACK_DEPTH_TYPE	 usStackDepth,	  /*任务分配的堆栈大小，单位为字(word)*/
    void * const 					pvParameters,	/*传递给任务函数的参数，一般为NULL*/
    UBaseType_t 					uxPriority,		/*任务优先级，范围:0~configMAX_PRIORITIES - 1*/
    TaskHandle_t * const 			 pxCreatedTask 	 /*任务句柄，就是这个任务控制块*/
                      )
```

```c
xReturn = pdPASS;//成功
xReturn = errCOULD_NOT_ALLOCATE_REQUIRED_MEMORY;//失败，申请堆栈太大
return xReturn;
```

### 操作流程

1. configSUPPORT_DYNAMIC_ALLOCATION = 1（默认）
2. 定义函数入口参数
3. 编写任务函数

- 创建结束后进入**就绪态**。

### 解析

```c
#if( configSUPPORT_DYNAMIC_ALLOCATION == 1 )

	BaseType_t xTaskCreate(	TaskFunction_t pxTaskCode,
							const char * const pcName,		/*lint !e971 Unqualified char types are allowed for strings and single characters only. */
							const configSTACK_DEPTH_TYPE usStackDepth,
							void * const pvParameters,
							UBaseType_t uxPriority,
							TaskHandle_t * const pxCreatedTask )
	{
	TCB_t *pxNewTCB;
	BaseType_t xReturn;

		/* If the stack grows down then allocate the stack then the TCB so the stack
		does not grow into the TCB.  Likewise if the stack grows up then allocate
		the TCB then the stack. */
        //判断堆栈，堆为向上生长，栈为向下生长。
		#if( portSTACK_GROWTH > 0 )
		{
			/* Allocate space for the TCB.  Where the memory comes from depends on
			the implementation of the port malloc function and whether or not static
			allocation is being used. */
			pxNewTCB = ( TCB_t * ) pvPortMalloc( sizeof( TCB_t ) );

			if( pxNewTCB != NULL )
			{
				/* Allocate space for the stack used by the task being created.
				The base of the stack memory stored in the TCB so the task can
				be deleted later if required. */
				pxNewTCB->pxStack = ( StackType_t * ) pvPortMalloc( ( ( ( size_t ) usStackDepth ) * sizeof( StackType_t ) ) ); /*lint !e961 MISRA exception as the casts are only redundant for some ports. */

				if( pxNewTCB->pxStack == NULL )
				{
					/* Could not allocate the stack.  Delete the allocated TCB. */
					vPortFree( pxNewTCB );
					pxNewTCB = NULL;
				}
			}
		}
		#else /* portSTACK_GROWTH */
		{
        //存放任务栈的首地址
		StackType_t *pxStack;
			
			/* Allocate space for the stack used by the task being created. */
            //系统帮我们申请地址
			pxStack = pvPortMalloc( ( ( ( size_t ) usStackDepth ) * sizeof( StackType_t ) ) ); /*lint !e9079 All values returned by pvPortMalloc() have at least the alignment required by the MCU's stack and this allocation is the stack. */

			if( pxStack != NULL )
			{
				/* Allocate space for the TCB. */
                //申请成功，则申请任务控制块
				pxNewTCB = ( TCB_t * ) pvPortMalloc( sizeof( TCB_t ) ); /*lint !e9087 !e9079 All values returned by pvPortMalloc() have at least the alignment required by the MCU's stack, and the first member of TCB_t is always a pointer to the task's stack. */

				if( pxNewTCB != NULL )
				{
					/* Store the stack location in the TCB. */
					pxNewTCB->pxStack = pxStack;
				}
				else
				{
					/* The stack cannot be used as the TCB was not created.  Free
					it again. */
					vPortFree( pxStack );
				}
			}
			else
			{
				pxNewTCB = NULL;
			}
		}
		#endif /* portSTACK_GROWTH */

		if( pxNewTCB != NULL )
		{
			#if( tskSTATIC_AND_DYNAMIC_ALLOCATION_POSSIBLE != 0 ) /*lint !e9029 !e731 Macro has been consolidated for readability reasons. */
			{
				/* Tasks can be created statically or dynamically, so note this
				task was created dynamically in case it is later deleted. */
                //标记这是动态生成的还是静态生成的
				pxNewTCB->ucStaticallyAllocated = tskDYNAMICALLY_ALLOCATED_STACK_AND_TCB;
			}
			#endif /* tskSTATIC_AND_DYNAMIC_ALLOCATION_POSSIBLE */
			//初始化任务控制块中的成员
			prvInitialiseNewTask( pxTaskCode, pcName, ( uint32_t ) usStackDepth, pvParameters, uxPriority, pxCreatedTask, pxNewTCB, NULL );
            //就绪
			prvAddNewTaskToReadyList( pxNewTCB );
			xReturn = pdPASS;
		}
		else
		{
			xReturn = errCOULD_NOT_ALLOCATE_REQUIRED_MEMORY;
		}

		return xReturn;
	}

#endif /* configSUPPORT_DYNAMIC_ALLOCATION */
```



## **`tskTCB`**

### 基本概念

`tskTCB` 是 FreeRTOS 用于管理任务的核心数据结构，每个任务都有一个对应的 TCB，相当于每个任务的身份证

```c
// 简化版的 tskTCB 结构（实际版本可能因配置而异）
typedef struct tskTaskControlBlock
{
    // 堆栈相关
    volatile StackType_t *pxTopOfStack;     // 当前堆栈顶指针
    StackType_t *pxStack;                   // 堆栈起始地址
    
    // 任务列表相关
    ListItem_t xStateListItem;              // 状态列表项（就绪、阻塞、挂起）
    ListItem_t xEventListItem;               // 事件列表项
    
    // 任务优先级
    UBaseType_t uxPriority;                 // 任务优先级
    UBaseType_t uxBasePriority;             // 基础优先级（用于优先级继承）
    
    // 任务标识
    TaskHandle_t xHandle;                   // 任务句柄
    const char *pcTaskName;                 // 任务名称
    
    // 堆栈信息
    configSTACK_DEPTH_TYPE usStackDepth;    // 堆栈深度
    
    // 任务状态
    eTaskState eCurrentState;               // 当前任务状态
    UBaseType_t uxCriticalNesting;          // 临界区嵌套计数
    
    // 调试和统计信息
    #if ( configUSE_TRACE_FACILITY == 1 )
        UBaseType_t uxTCBNumber;            // TCB 编号（调试用）
    #endif
        
    #if ( configGENERATE_RUN_TIME_STATS == 1 )
        uint32_t ulRunTimeCounter;          // 运行时间统计
    #endif
        
    // 其他扩展字段...
} tskTCB;

// 在 FreeRTOS 中，tskTCB 通常被重定义为 TCB_t
typedef tskTCB TCB_t;
```

### 与任务句柄关系

```c
typedef struct tskTaskControlBlock * TaskHandle_t;
TaskHandle_t CurrentTask;
CurrenTask->pcTaskName;
```

可见，任务句柄就是指向TCB的结构体指针。

## **`xTaskCreateStatic()`**
静态创建任务

```c
TaskHandle_t xTaskCreateStatic(
    TaskFunction_t pxTaskCode,        //任务函数指针
    const char * const pcName,        //任务名称字符串
    uint32_t ulStackDepth,            //堆栈深度（以字为单位）
    void *pvParameters,               //传递给任务函数的参数
    UBaseType_t uxPriority,           //任务优先级
    StackType_t *puxStackBuffer,      //堆栈缓冲区指针
    StaticTask_t *pxTaskBuffer        //TCB缓冲区指针
);
```

### 操作流程

1. configSUPPORT_STATIC_ALLOCATION = 1
2. 定义空闲任务（必须）&定时器任务（可选）的任务堆栈及TCB
3. 实现两个接口函数（`vApplicationGetIdleTaskMemory`和 `vApplicationGetTimerTaskMemory`）
4. 定义函数入口参数
5. 编写任务函数

## **`vTaskDelete()`**

```c
void vTaskDelete(TaskHandle_t xTaskToDelete);
```

> [!NOTE]
>
> 1. 当传入的位NULL时，会删除任务自己，即当前正在运行的任务。
> 2. 空闲任务负责释放被删除任务中由系统分配的内存，但那些由任务静态创建自己分配的内存要用户提前释放，否则会导致**内存泄漏**

### 流程

1. INCLUDE_vTaskDelete = 1
2. 使用函数，传入句柄。

## **`vTaskStartScheduler()`**

开启任务调度。需要在创建完所有任务后启用。

### 函数执行的主要步骤：

```c
void vTaskStartScheduler( void )
{
    // 1. 创建空闲任务 (IDLE Task)
    xIdleTaskHandle = xTaskCreate( 
        prvIdleTask, 
        "IDLE", 
        configMINIMAL_STACK_SIZE, 
        NULL, 
        tskIDLE_PRIORITY, 
        &xIdleTaskHandle 
    );
    
    #if ( configUSE_TIMERS == 1 )
    // 2. 如果启用软件定时器，创建定时器服务任务
    xTimerTaskHandle = xTaskCreate( 
        prvTimerTask, 
        "Tmr Svc", 
        configTIMER_TASK_STACK_DEPTH, 
        NULL, 
        configTIMER_TASK_PRIORITY, 
        &xTimerTaskHandle 
    );
    #endif
    
    // 3. 初始化系统节拍定时器 (Systick)
    if( xPortStartScheduler() != pdFALSE )
    {
        // 4. 开始第一个任务的执行
        // 这里不会返回
    }
    else
    {
        // 5. 调度器启动失败
    }
}
```

#  2. **CMSIS-RTOS v2** API

**CMSIS-RTOS** 是ARM指定的用于兼容不同RTOS的API规范。

---

##  **核心创建函数：`osThreadNew()`**

```c
osThreadId_t osThreadNew(osThreadFunc_t func, void *argument, const osThreadAttr_t *attr);
```

**参数说明：**

- `func`：线程函数指针（线程执行的代码）
- `argument`：传递给线程函数的参数
- `attr`：线程属性结构体指针（可为 NULL 使用默认值）

**返回值：**

- 成功：返回线程 ID (`osThreadId_t`)
- 失败：返回 `NULL`

###  线程属性结构体：`osThreadAttr_t`

```c
typedef struct {
  const char                   *name;        // 线程名称
  uint32_t                 attr_bits;        // 属性位osThreadDetached（线程终止时自动清理资源）、osThreadJoinable（线程可被其他线程等待）等
  void                      *cb_mem;         // 控制块内存
  uint32_t                   cb_size;        // 控制块大小
  void                   *stack_mem;         // 栈内存
  uint32_t                stack_size;        // 栈大小（字节）
  osPriority_t              priority;        // 优先级
  TZ_ModuleId_t            tz_module;        // TrustZone 模块 ID
  uint32_t                  reserved;        // 保留
} osThreadAttr_t;
```

#### 默认值规则

如果`attr`的某些参数为 `NULL` 或 `0`，系统会使用默认值：

| 参数        | 默认值             |
| :---------- | :----------------- |
| `name`      | 系统生成的名称     |
| `attr_bits` | `osThreadDetached` |
| `cb_mem`    | 动态分配控制块     |
| `stack_mem` | 动态分配栈内存     |
| `priority`  | `osPriorityNormal` |
| `tz_module` | 非安全域           |
| `reserved`  | 必须为 0           |

## **线程删除**

### 1. **终止线程：`osThreadTerminate()`**

```c
osStatus_t osThreadTerminate(osThreadId_t thread_id);
```

**参数：**

- `thread_id`：要终止的线程 ID

**返回值：**

- `osOK`：成功
- `osErrorParameter`：参数错误
- `osErrorResource`：线程不存在

### 2. **退出当前线程：`osThreadExit()`**

```c
void osThreadExit(void);
```

**说明：** 在线程内部调用，用于自我终止。

## **开启任务调度**

```c
osKernelStart();	
```

