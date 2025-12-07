队列、信号量、互斥量都是多对多，我们不知道是谁在参与。如果我们想单独通知一个特定的任务怎么办呢？使用**任务通知**
# 任务通知的基本概念

## 什么是任务通知

任务通知是FreeRTOS中最高效的轻量级通信机制，可以理解为每个任务自带的"邮箱"：

- **每个任务都有一个内置的通知值**：就像每个人都有一个专属收件箱
- **直接通知目标任务**：无需创建中间对象，直接向目标任务的"邮箱"投递消息
- **多种通信模式**：可以模拟二进制信号量、计数信号量、事件组、轻量级队列

## 任务通知的形象比喻

**邮箱系统**：
- 每个任务就像有一个专属邮箱（通知值）
- 其他任务可以直接向这个邮箱投递信件（发送通知）
- 任务可以随时检查自己的邮箱（接收通知）
- 邮箱可以设置不同的接收规则（通知动作）

# 任务通知的核心特点

## 性能优势

**速度最快**：
- 比队列快45%
- 比二进制信号量快45%
- 比计数信号量快10%

**内存开销最小**：
- 每个任务只需要额外8字节存储通知值
- 无需创建独立的消息对象
- 零内存分配开销

## 功能特性

**灵活性高**：
- 可以模拟多种通信机制
- 支持数据传递和事件通知
- 提供丰富的通知动作选项

**直接通信**：
- 一对一通信模式
- 无需中间通信对象
- 直接操作目标任务状态

## 局限性

- **只能一对一通信**：一个通知只能发给一个特定任务
- **无存储队列**：只能保存一个通知值，新通知可能覆盖旧值
- **需要知道目标任务句柄**：必须持有目标任务的TaskHandle_t

# FreeRTOS任务通知操作函数

## 发送通知函数

### xTaskNotify - 通用通知发送
```c
BaseType_t xTaskNotify(TaskHandle_t xTaskToNotify, 
                      uint32_t ulValue, 
                      eNotifyAction eAction);
```

**参数说明**：
- `xTaskToNotify`：目标任务句柄
- `ulValue`：通知值
- `eAction`：通知动作类型

**通知动作类型**：
```c
typedef enum {
    eNoAction = 0,           // 仅更新通知状态，不修改通知值
    eSetBits,                // 设置通知值的指定位
    eIncrement,              // 递增通知值
    eSetValueWithOverwrite,  // 直接覆盖通知值
    eSetValueWithoutOverwrite // 仅在通知未处理时覆盖
} eNotifyAction;
```

### xTaskNotifyFromISR - 中断中发送通知
```c
BaseType_t xTaskNotifyFromISR(TaskHandle_t xTaskToNotify,
                             uint32_t ulValue,
                             eNotifyAction eAction,
                             BaseType_t *pxHigherPriorityTaskWoken);
```

### xTaskNotifyGive - 轻量级信号量发送
```c
void xTaskNotifyGive(TaskHandle_t xTaskToNotify);
```
相当于`xTaskNotify(xTaskToNotify, 0, eIncrement)`

### xTaskNotifyAndQuery - 带查询的发送
```c
BaseType_t xTaskNotifyAndQuery(TaskHandle_t xTaskToNotify,
                              uint32_t ulValue,
                              eNotifyAction eAction,
                              uint32_t *pulPreviousNotifyValue);
```

## 接收通知函数

### ulTaskNotifyTake - 轻量级信号量接收
```c
uint32_t ulTaskNotifyTake(BaseType_t xClearCountOnExit,
                         TickType_t xTicksToWait);
```
专为模拟信号量设计，返回通知值的当前值。

### xTaskNotifyWait - 通用通知接收
```c
BaseType_t xTaskNotifyWait(uint32_t ulBitsToClearOnEntry,
                          uint32_t ulBitsToClearOnExit,
                          uint32_t *pulNotificationValue,
                          TickType_t xTicksToWait);
```
功能最全面的通知接收函数，支持位操作和数据获取。

## 查询函数

### uxTaskNotifyGetCounter - 获取通知计数器
```c
uint32_t uxTaskNotifyGetCounter(TaskHandle_t xTask);
```

### xTaskNotifyStateClear - 清除通知状态
```c
BaseType_t xTaskNotifyStateClear(TaskHandle_t xTask);
```

# FreeRTOS任务通知使用模式

## 模式1：模拟二进制信号量

**发送方**：
```c
void vSenderTask(void *pvParameters) {
    TaskHandle_t xReceiverHandle = (TaskHandle_t)pvParameters;
    
    while(1) {
        // 完成工作后通知接收方
        do_work();
        
        // 发送通知（相当于give信号量）
        xTaskNotifyGive(xReceiverHandle);
        
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}
```

**接收方**：
```c
void vReceiverTask(void *pvParameters) {
    uint32_t ulNotificationValue;
    
    while(1) {
        // 等待通知（相当于take信号量）
        ulNotificationValue = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        if(ulNotificationValue > 0) {
            // 处理工作
            process_work();
        }
    }
}
```

## 模式2：模拟事件组

**发送方**：
```c
void vEventSenderTask(void *pvParameters) {
    TaskHandle_t xProcessorHandle = (TaskHandle_t)pvParameters;
    
    while(1) {
        // 设置不同的事件位
        if(sensor1_ready()) {
            xTaskNotify(xProcessorHandle, (1UL << 0), eSetBits);  // 事件位0
        }
        
        if(sensor2_ready()) {
            xTaskNotify(xProcessorHandle, (1UL << 1), eSetBits);  // 事件位1
        }
        
        vTaskDelay(50 / portTICK_PERIOD_MS);
    }
}
```

**接收方**：
```c
void vEventProcessorTask(void *pvParameters) {
    uint32_t ulNotifiedValue;
    const uint32_t ALL_EVENTS_MASK = (1UL << 0) | (1UL << 1);
    
    while(1) {
        // 等待特定事件位
        xTaskNotifyWait(0,                          // 进入时不清除位
                       ALL_EVENTS_MASK,            // 退出时清除所有事件位
                       &ulNotifiedValue,           // 获取通知值
                       portMAX_DELAY);
        
        if((ulNotifiedValue & ALL_EVENTS_MASK) == ALL_EVENTS_MASK) {
            printf("All events received!\n");
            process_all_events();
        } else if(ulNotifiedValue & (1UL << 0)) {
            printf("Event 0 received\n");
            process_event_0();
        } else if(ulNotifiedValue & (1UL << 1)) {
            printf("Event 1 received\n");
            process_event_1();
        }
    }
}
```

## 模式3：数据传递

**发送方**：
```c
void vDataSenderTask(void *pvParameters) {
    TaskHandle_t xReceiverHandle = (TaskHandle_t)pvParameters;
    uint32_t data_counter = 0;
    
    while(1) {
        // 准备数据
        uint32_t data_packet = (data_counter++ & 0xFFFFFF) | (1UL << 31);
        
        // 发送数据（覆盖模式）
        xTaskNotify(xReceiverHandle, data_packet, eSetValueWithOverwrite);
        
        vTaskDelay(200 / portTICK_PERIOD_MS);
    }
}
```

**接收方**：
```c
void vDataReceiverTask(void *pvParameters) {
    uint32_t received_data;
    
    while(1) {
        // 接收数据
        if(xTaskNotifyWait(0, 0, &received_data, 1000 / portTICK_PERIOD_MS) == pdTRUE) {
            if(received_data & (1UL << 31)) {
                uint32_t actual_data = received_data & 0xFFFFFF;
                printf("Received data: %lu\n", actual_data);
            }
        } else {
            printf("No data received within timeout\n");
        }
    }
}
```

## 模式4：计数信号量

**发送方**：
```c
void vResourceProducerTask(void *pvParameters) {
    TaskHandle_t xConsumerHandle = (TaskHandle_t)pvParameters;
    
    while(1) {
        // 生产多个资源
        for(int i = 0; i < 3; i++) {
            xTaskNotifyGive(xConsumerHandle);  // 增加计数
        }
        
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}
```

**接收方**：
```c
void vResourceConsumerTask(void *pvParameters) {
    uint32_t available_resources;
    
    while(1) {
        // 获取可用资源数量（不清除计数）
        available_resources = ulTaskNotifyTake(pdFALSE, 0);
        
        if(available_resources > 0) {
            // 使用一个资源（减少计数）
            ulTaskNotifyTake(pdTRUE, 0);
            
            printf("Using resource, %lu remaining\n", available_resources - 1);
            use_resource();
        } else {
            // 等待资源可用
            available_resources = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
            printf("Resource acquired, now using\n");
            use_resource();
        }
        
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}
```
# 任务通知最佳实践

## 使用场景选择

**适合使用任务通知的场景**：
- 一对一任务通信
- 轻量级同步需求
- 性能敏感的应用
- 内存受限的系统
- 简单的数据传递

**不适合使用任务通知的场景**：
- 一对多通信（使用事件组或队列）
- 需要存储多个消息（使用队列）
- 多个任务等待同一资源（使用信号量/互斥量）
- 复杂的数据结构传递（使用队列）

## 性能优化技巧

**减少通知丢失**：
```c
// 使用不覆盖模式保护重要数据
xTaskNotify(xTargetTask, important_data, eSetValueWithoutOverwrite);

// 使用位操作累加事件
xTaskNotify(xTargetTask, event_mask, eSetBits);
```

**合理选择通知动作**：
```c
// 同步场景 - 使用递增
xTaskNotifyGive(xTargetTask);

// 事件场景 - 使用位设置  
xTaskNotify(xTargetTask, EVENT_MASK, eSetBits);

// 数据传递 - 使用覆盖
xTaskNotify(xTargetTask, data_value, eSetValueWithOverwrite);
```

## 错误处理策略

**检查发送结果**：
```c
BaseType_t result = xTaskNotify(xTargetTask, value, action);
if(result != pdPASS) {
    // 处理发送失败
    handle_notification_failure();
}
```

**处理接收超时**：
```c
if(xTaskNotifyWait(ulBitsToClearOnEntry, ulBitsToClearOnExit, 
                   &ulNotifiedValue, reasonable_timeout) != pdTRUE) {
    // 处理超时情况
    handle_notification_timeout();
}
```
# CMSIS-RTOS v2 任务通知等效机制

## CMSIS-RTOS v2 中的任务通知替代方案

CMSIS-RTOS v2 **没有直接等效的任务通知机制**，但提供了**线程标志（Thread Flags）** 作为最接近的替代方案。线程标志提供了类似任务通知的功能，但实现方式有所不同。

## 线程标志（Thread Flags）

### 线程标志的基本概念

线程标志是CMSIS-RTOS v2中每个线程自带的32位标志寄存器，具有以下特点：

- **每个线程都有32个标志位**：每个线程拥有独立的32位标志寄存器
- **直接线程间通信**：任何线程都可以设置其他线程的标志位
- **多种等待选项**：支持等待任意标志、所有标志或特定组合
- **无存储限制**：不会像FreeRTOS任务通知那样被新值覆盖

### 线程标志 vs FreeRTOS任务通知

| 特性 | FreeRTOS任务通知 | CMSIS-RTOS v2线程标志 |
|------|------------------|----------------------|
| 存储大小 | 32位值 | 32个独立标志位 |
| 数据传递 | 可以传递32位数据 | 只能传递标志位状态 |
| 覆盖行为 | 可能被新通知覆盖 | 标志位可以独立设置/清除 |
| 通知动作 | 多种动作类型 | 只有设置标志位 |
| 性能 | 非常高 | 高 |
| 灵活性 | 中等 | 高（32个独立标志） |

### CMSIS-RTOS v2 线程标志函数

#### osThreadFlagsSet - 设置线程标志
```c
uint32_t osThreadFlagsSet(osThreadId_t thread_id, uint32_t flags);
```

**参数**：
- `thread_id`：目标线程ID
- `flags`：要设置的标志位掩码

**返回值**：
- 成功：设置后线程的标志位状态
- 失败：最高位为1的错误代码

**使用示例**：
```c
// 设置线程的标志位0和2
uint32_t result = osThreadFlagsSet(target_thread, (1UL << 0) | (1UL << 2));
if((result & 0x80000000) == 0) {
    printf("Flags set successfully, current flags: 0x%08lX\n", result);
} else {
    printf("Failed to set flags: error 0x%08lX\n", result);
}
```

#### osThreadFlagsWait - 等待线程标志
```c
uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout);
```

**参数**：
- `flags`：要等待的标志位掩码
- `options`：等待选项
- `timeout`：超时时间（毫秒）

**等待选项**：
```c
osFlagsWaitAny    // 等待任意指定标志位
osFlagsWaitAll    // 等待所有指定标志位
osFlagsNoClear    // 等待后不清除标志位
```

**使用示例**：
```c
// 等待标志位0或1（任意一个）
uint32_t received_flags = osThreadFlagsWait((1UL << 0) | (1UL << 1), 
                                           osFlagsWaitAny, 
                                           osWaitForever);

// 等待标志位2和3（两个都必须设置）
uint32_t received_flags = osThreadFlagsWait((1UL << 2) | (1UL << 3),
                                           osFlagsWaitAll,
                                           5000);  // 5秒超时
```

#### osThreadFlagsClear - 清除线程标志
```c
uint32_t osThreadFlagsClear(uint32_t flags);
```

#### osThreadFlagsGet - 获取当前线程标志状态
```c
uint32_t osThreadFlagsGet(void);
```

### 辅助函数

#### osThreadGetId - 获取当前线程ID
```c
osThreadId_t osThreadGetId(void);
```

## 线程标志使用模式

## 模式1：模拟二进制信号量

**FreeRTOS任务通知方式**：
```c
// 发送方
xTaskNotifyGive(xReceiverTask);

// 接收方
ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
```

**CMSIS-RTOS v2线程标志方式**：
```c
// 发送方
osThreadFlagsSet(receiver_thread, 0x01);  // 使用标志位0作为信号量

// 接收方
osThreadFlagsWait(0x01, osFlagsWaitAny, osWaitForever);  // 等待后自动清除
```

## 模式2：模拟事件组

**FreeRTOS任务通知方式**：
```c
// 发送方
xTaskNotify(xTargetTask, (1UL << 0) | (1UL << 2), eSetBits);

// 接收方
xTaskNotifyWait(0, (1UL << 0) | (1UL << 2), &value, portMAX_DELAY);
```

**CMSIS-RTOS v2线程标志方式**：
```c
// 发送方
osThreadFlagsSet(target_thread, (1UL << 0) | (1UL << 2));

// 接收方
uint32_t flags = osThreadFlagsWait((1UL << 0) | (1UL << 2), 
                                  osFlagsWaitAny, 
                                  osWaitForever);
```

## 模式3：多事件分离处理

**CMSIS-RTOS v2特有优势**：
```c
void event_handler_thread(void *argument) {
    uint32_t flags;
    
    while(1) {
        // 等待多种类型的事件
        flags = osThreadFlagsWait(0x000000FF, osFlagsWaitAny, osWaitForever);
        
        // 根据具体标志位处理不同事件
        if(flags & 0x01) {
            handle_temperature_event();
            osThreadFlagsClear(0x01);  // 明确清除已处理的事件
        }
        if(flags & 0x02) {
            handle_humidity_event();
            osThreadFlagsClear(0x02);
        }
        if(flags & 0x04) {
            handle_pressure_event();
            osThreadFlagsClear(0x04);
        }
        if(flags & 0x08) {
            handle_system_event();
            osThreadFlagsClear(0x08);
        }
        // ... 可以处理最多32种独立事件
    }
}
```

## 线程标志高级用法

### 标志位管理策略

#### 按功能分组标志位
```c
// 传感器相关标志（低8位）
#define SENSOR_MASK          0x000000FF
#define TEMPERATURE_EVENT    (1UL << 0)
#define HUMIDITY_EVENT       (1UL << 1)
#define PRESSURE_EVENT       (1UL << 2)

// 系统事件标志（中8位）  
#define SYSTEM_MASK          0x0000FF00
#define SYSTEM_ALERT         (1UL << 8)
#define CONFIG_CHANGE        (1UL << 9)
#define DATA_BACKUP          (1UL << 10)

// 用户事件标志（高8位）
#define USER_MASK           0x00FF0000
#define USER_INPUT           (1UL << 16)
#define DISPLAY_UPDATE       (1UL << 17)
```

#### 多条件等待
```c
void advanced_wait_example(void) {
    uint32_t flags;
    
    // 方案1：等待任意传感器事件或系统警报
    flags = osThreadFlagsWait(SENSOR_MASK | SYSTEM_ALERT, 
                             osFlagsWaitAny, 
                             osWaitForever);
    
    // 方案2：等待温度+湿度事件同时发生
    flags = osThreadFlagsWait(TEMPERATURE_EVENT | HUMIDITY_EVENT,
                             osFlagsWaitAll,
                             1000);  // 1秒超时
                             
    // 方案3：等待但不清除标志（用于监控）
    flags = osThreadFlagsWait(USER_INPUT, 
                             osFlagsWaitAny | osFlagsNoClear,
                             500);
}
```

### 错误处理最佳实践

#### 检查函数返回值
```c
uint32_t result = osThreadFlagsSet(target_thread, flags);
if(result & 0x80000000) {
    // 处理错误
    switch(result) {
        case osErrorParameter:
            printf("Error: Invalid thread ID or flags\n");
            break;
        case osErrorResource:
            printf("Error: Thread flags resource not available\n");
            break;
        case osErrorISR:
            printf("Error: Cannot call from ISR context\n");
            break;
        default:
            printf("Error: Unknown error (0x%08lX)\n", result);
    }
}
```

#### 超时处理策略
```c
uint32_t flags = osThreadFlagsWait(EVENT_MASK, osFlagsWaitAny, timeout_ms);
if((flags & 0x80000000) == 0) {
    // 成功接收到标志
    process_events(flags);
} else {
    // 超时或其他错误
    if(flags == osErrorTimeout) {
        handle_timeout();
    } else {
        handle_error(flags);
    }
}
```

## 与FreeRTOS任务通知的迁移指南

## 函数映射表

| FreeRTOS任务通知 | CMSIS-RTOS v2线程标志 | 说明 |
|------------------|----------------------|------|
| `xTaskNotifyGive()` | `osThreadFlagsSet(thread, 0x01)` | 简单信号量模拟 |
| `ulTaskNotifyTake(pdTRUE, timeout)` | `osThreadFlagsWait(0x01, osFlagsWaitAny, timeout)` | 接收并清除 |
| `xTaskNotify(task, value, eSetBits)` | `osThreadFlagsSet(thread, flags)` | 设置标志位 |
| `xTaskNotifyWait(0, mask, &value, timeout)` | `osThreadFlagsWait(mask, osFlagsWaitAny, timeout)` | 等待标志位 |
| `uxTaskNotifyGetCounter()` | `osThreadFlagsGet()` | 获取当前标志状态 |

## 迁移注意事项

### 数据传递差异
```c
// FreeRTOS：可以传递32位数据
uint32_t sensor_data = 0x12345678;
xTaskNotify(xProcessor, sensor_data, eSetValueWithOverwrite);

// CMSIS-RTOS v2：只能传递标志位状态，需要其他方式传递数据
// 方案1：使用消息队列传递数据
osMessageQueuePut(data_queue, &sensor_data, 0, 0);
osThreadFlagsSet(processor_thread, DATA_READY_FLAG);

// 方案2：使用全局变量+标志位
g_sensor_data = sensor_data;
osThreadFlagsSet(processor_thread, DATA_READY_FLAG);
```

### 覆盖行为差异
```c
// FreeRTOS：新通知可能覆盖旧值
xTaskNotify(xTask, value1, eSetValueWithOverwrite);  // 可能丢失value1
xTaskNotify(xTask, value2, eSetValueWithOverwrite);

// CMSIS-RTOS v2：标志位可以累积，不会被覆盖
osThreadFlagsSet(thread, FLAG1);  // FLAG1保持设置
osThreadFlagsSet(thread, FLAG2);  // FLAG1和FLAG2都保持设置
```

## 性能考虑

**CMSIS-RTOS v2线程标志的优势**：
- 32个独立标志位，不会相互覆盖
- 标志位状态持久化，直到显式清除
- 支持复杂的等待条件组合

**FreeRTOS任务通知的优势**：
- 可以传递32位任意数据
- 更灵活的通知动作类型
- 略微更好的性能