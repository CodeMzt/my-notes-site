# 事件组的基本概念

## 什么是事件组

事件组是一种用于多任务同步的机制，允许任务等待多个事件中的任意一个或全部发生。可以理解为**多条件等待系统**：

- **每个事件用一个位表示**：32位系统支持32个独立事件
- **任务可以等待事件组合**：可以等待任意事件、所有事件或特定事件组合
- **事件状态持久化**：事件一旦发生就会保持，直到被显式清除
- **多任务可以等待相同事件**：支持一对多的通知机制

## 事件组的形象比喻

**机场航班信息牌**：
- 每个航班状态用一个指示灯表示（事件位）
- 旅客可以等待特定航班（等待单个事件）
- 接机人员可以等待多个航班中的任意一个（等待任意事件）
- 旅行团领队需要等待所有团员航班到达（等待所有事件）
- 航班到达后指示灯保持亮起，直到被重置（事件持久化）

# 事件组的核心特点

## 优势特性

**多条件等待**：
- 可以同时等待多个事件条件
- 支持"任意事件"和"所有事件"两种等待模式
- 灵活的事件组合条件

**广播通知**：
- 一个事件可以唤醒多个等待的任务
- 支持一对多的通信模式
- 高效的事件分发机制

**无丢失事件**：
- 事件状态会一直保持
- 不会被新事件覆盖
- 确保不会错过重要事件

## 适用场景

**多传感器数据收集**：
```c
// 等待温度、湿度、压力传感器数据全部就绪
xEventGroupWaitBits(events, TEMP_READY | HUMID_READY | PRESS_READY, 
                   pdTRUE, pdTRUE, portMAX_DELAY);
```

**系统状态监控**：
```c
// 等待任意错误事件发生
xEventGroupWaitBits(events, ERROR_MASK, pdTRUE, pdFALSE, portMAX_DELAY);
```

**多阶段初始化**：
```c
// 等待所有子系统初始化完成
xEventGroupWaitBits(events, INIT_MASK, pdTRUE, pdTRUE, portMAX_DELAY);
```

# FreeRTOS事件组操作函数

## 创建和删除函数

### xEventGroupCreate - 创建事件组
```c
EventGroupHandle_t xEventGroupCreate(void);
```

**返回值**：
- 成功：事件组句柄
- 失败：NULL（内存不足时）

**创建示例**：
```c
EventGroupHandle_t xSystemEvents;

void vInitializeEventGroups(void) {
    xSystemEvents = xEventGroupCreate();
    if(xSystemEvents == NULL) {
        printf("ERROR: Failed to create system events group\n");
    } else {
        printf("System events group created successfully\n");
    }
}
```

### xEventGroupCreateStatic - 静态创建
```c
EventGroupHandle_t xEventGroupCreateStatic(StaticEventGroup_t *pxEventGroupBuffer);
```

### vEventGroupDelete - 删除事件组
```c
void vEventGroupDelete(EventGroupHandle_t xEventGroup);
```

## 事件设置函数

### xEventGroupSetBits - 设置事件位
```c
EventBits_t xEventGroupSetBits(EventGroupHandle_t xEventGroup,
                              const EventBits_t uxBitsToSet);
```

**功能**：设置指定的事件位，并返回设置后的事件组状态

**使用示例**：
```c
// 设置温度传感器就绪事件
EventBits_t current_bits = xEventGroupSetBits(xSystemEvents, TEMP_READY_BIT);
printf("Event bits after setting: 0x%08lX\n", current_bits);
```

### xEventGroupSetBitsFromISR - 中断中设置事件位
```c
BaseType_t xEventGroupSetBitsFromISR(EventGroupHandle_t xEventGroup,
                                    const EventBits_t uxBitsToSet,
                                    BaseType_t *pxHigherPriorityTaskWoken);
```

## 事件等待函数

### xEventGroupWaitBits - 等待事件位
```c
EventBits_t xEventGroupWaitBits(EventGroupHandle_t xEventGroup,
                               const EventBits_t uxBitsToWaitFor,
                               const BaseType_t xClearOnExit,
                               const BaseType_t xWaitForAllBits,
                               TickType_t xTicksToWait);
```

**参数详解**：
- `uxBitsToWaitFor`：要等待的事件位掩码
- `xClearOnExit`：退出时是否清除等待的事件位
  - `pdTRUE`：成功等待后清除这些事件位
  - `pdFALSE`：保持事件位状态不变
- `xWaitForAllBits`：等待模式
  - `pdTRUE`：等待所有指定事件位都设置
  - `pdFALSE`：等待任意指定事件位设置
- `xTicksToWait`：超时时间

**返回值**：
- 成功：满足条件的事件位状态
- 超时：超时时刻的事件位状态（可能不满足等待条件）

## 事件清除函数

### xEventGroupClearBits - 清除事件位
```c
EventBits_t xEventGroupClearBits(EventGroupHandle_t xEventGroup,
                                const EventBits_t uxBitsToClear);
```

### xEventGroupClearBitsFromISR - 中断中清除事件位
```c
BaseType_t xEventGroupClearBitsFromISR(EventGroupHandle_t xEventGroup,
                                      const EventBits_t uxBitsToClear);
```

## 事件查询函数

### xEventGroupGetBits - 获取当前事件位状态
```c
EventBits_t xEventGroupGetBits(EventGroupHandle_t xEventGroup);
```

### xEventGroupGetBitsFromISR - 中断中获取事件位状态
```c
EventBits_t xEventGroupGetBitsFromISR(EventGroupHandle_t xEventGroup);
```

## 同步操作函数

### xEventGroupSync - 事件组同步
```c
EventBits_t xEventGroupSync(EventGroupHandle_t xEventGroup,
                           const EventBits_t uxBitsToSet,
                           const EventBits_t uxBitsToWaitFor,
                           TickType_t xTicksToWait);
```

**特殊功能**：原子操作，先设置指定事件位，然后等待指定事件位条件

# FreeRTOS事件组使用模式

## 模式1：多条件等待（AND条件）

```c
// 定义事件位
#define SENSOR_TEMP_READY    (1UL << 0)
#define SENSOR_HUMID_READY   (1UL << 1)
#define SENSOR_PRESS_READY   (1UL << 2)
#define ALL_SENSORS_READY    (SENSOR_TEMP_READY | SENSOR_HUMID_READY | SENSOR_PRESS_READY)

void vDataFusionTask(void *pvParameters) {
    EventBits_t uxBits;
    
    while(1) {
        // 等待所有传感器数据就绪
        uxBits = xEventGroupWaitBits(xSensorEvents, 
                                    ALL_SENSORS_READY,    // 等待的事件位
                                    pdTRUE,              // 成功等待后清除这些位
                                    pdTRUE,              // 需要等待所有位
                                    portMAX_DELAY);      // 无限期等待
        
        if((uxBits & ALL_SENSORS_READY) == ALL_SENSORS_READY) {
            // 所有传感器数据都已就绪，进行数据融合
            perform_data_fusion();
            printf("Data fusion completed\n");
        }
    }
}

void vTemperatureSensorTask(void *pvParameters) {
    while(1) {
        // 读取温度传感器
        read_temperature_sensor();
        
        // 设置温度就绪事件
        xEventGroupSetBits(xSensorEvents, SENSOR_TEMP_READY);
        
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}
```

## 模式2：任意条件等待（OR条件）

```c
#define NETWORK_CONNECTED    (1UL << 0)
#define BLUETOOTH_CONNECTED  (1UL << 1)
#define SERIAL_CONNECTED     (1UL << 2)
#define ANY_CONNECTION       (NETWORK_CONNECTED | BLUETOOTH_CONNECTED | SERIAL_CONNECTED)

void vCommunicationTask(void *pvParameters) {
    EventBits_t uxBits;
    
    while(1) {
        // 等待任意连接建立
        uxBits = xEventGroupWaitBits(xCommEvents,
                                    ANY_CONNECTION,      // 等待任意连接事件
                                    pdFALSE,            // 不清除事件位
                                    pdFALSE,            // 任意事件位设置即可
                                    portMAX_DELAY);
        
        // 检查具体哪个连接就绪
        if(uxBits & NETWORK_CONNECTED) {
            printf("Network connection established\n");
            handle_network_communication();
        }
        if(uxBits & BLUETOOTH_CONNECTED) {
            printf("Bluetooth connection established\n");
            handle_bluetooth_communication();
        }
        if(uxBits & SERIAL_CONNECTED) {
            printf("Serial connection established\n");
            handle_serial_communication();
        }
    }
}
```

## 模式3：事件组同步

```c
#define TASK1_COMPLETE       (1UL << 0)
#define TASK2_COMPLETE       (1UL << 1)
#define TASK3_COMPLETE       (1UL << 2)
#define ALL_TASKS_COMPLETE   (TASK1_COMPLETE | TASK2_COMPLETE | TASK3_COMPLETE)

void vSynchronizationTask(void *pvParameters) {
    EventBits_t uxBits;
    
    while(1) {
        // 使用同步功能：设置自己的完成位，并等待所有任务完成
        uxBits = xEventGroupSync(xSyncEvents,
                                TASK1_COMPLETE,         // 设置自己的完成位
                                ALL_TASKS_COMPLETE,     // 等待所有任务完成
                                portMAX_DELAY);
        
        // 所有任务都已完成，执行同步后操作
        printf("All tasks synchronized, performing collective operation\n");
        perform_collective_operation();
        
        // 清除所有完成位，准备下一轮同步
        xEventGroupClearBits(xSyncEvents, ALL_TASKS_COMPLETE);
        
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}
```

# CMSIS-RTOS v2 事件标志等效功能

## CMSIS-RTOS v2 事件标志

CMSIS-RTOS v2 使用**事件标志（Event Flags）** 对象来提供类似FreeRTOS事件组的功能。

## 事件标志函数对照表

| FreeRTOS事件组 | CMSIS-RTOS v2事件标志 | 说明 |
|----------------|----------------------|------|
| `xEventGroupCreate()` | `osEventFlagsNew()` | 创建事件标志对象 |
| `vEventGroupDelete()` | `osEventFlagsDelete()` | 删除事件标志对象 |
| `xEventGroupSetBits()` | `osEventFlagsSet()` | 设置事件标志 |
| `xEventGroupClearBits()` | `osEventFlagsClear()` | 清除事件标志 |
| `xEventGroupWaitBits()` | `osEventFlagsWait()` | 等待事件标志 |
| `xEventGroupGetBits()` | `osEventFlagsGet()` | 获取当前事件标志状态 |
| `xEventGroupSync()` | 无直接等效 | 需要手动实现 |

## CMSIS-RTOS v2 事件标志详细函数

### osEventFlagsNew - 创建事件标志
```c
osEventFlagsId_t osEventFlagsNew(const osEventFlagsAttr_t *attr);
```

**创建示例**：
```c
osEventFlagsId_t system_events;

void initialize_event_flags(void) {
    osEventFlagsAttr_t event_attr = {
        .name = "SystemEvents"
    };
    system_events = osEventFlagsNew(&event_attr);
    
    if(system_events == NULL) {
        printf("ERROR: Failed to create event flags\n");
    }
}
```

### osEventFlagsSet - 设置事件标志
```c
uint32_t osEventFlagsSet(osEventFlagsId_t ef_id, uint32_t flags);
```

- `flags` 对应事件标志位，比如0000 0010 就是对应第二个事件。若第二个事件发生，则会返回该位为1的结果。
### osEventFlagsClear - 清除事件标志
```c
uint32_t osEventFlagsClear(osEventFlagsId_t ef_id, uint32_t flags);
```

### osEventFlagsWait - 等待事件标志
```c
uint32_t osEventFlagsWait(osEventFlagsId_t ef_id, uint32_t flags, uint32_t options, uint32_t timeout);
```

**等待选项**：
```c
osFlagsWaitAny    // 等待任意指定标志
osFlagsWaitAll    // 等待所有指定标志
osFlagsNoClear    // 等待后不清除标志
```

### osEventFlagsGet - 获取事件标志状态
```c
uint32_t osEventFlagsGet(osEventFlagsId_t ef_id);
```

### osEventFlagsDelete - 删除事件标志
```c
osStatus_t osEventFlagsDelete(osEventFlagsId_t ef_id);
```


# 事件组/事件标志最佳实践

## 设计原则

**合理规划事件位**：
```c
// 按功能分组事件位
#define SENSOR_EVENTS   0x000000FF  // 低8位：传感器事件
#define NETWORK_EVENTS  0x0000FF00  // 中8位：网络事件  
#define SYSTEM_EVENTS   0x00FF0000  // 高8位：系统事件
#define USER_EVENTS     0xFF000000  // 最高8位：用户事件
```

**避免事件位冲突**：
```c
// 不好的做法：随意使用事件位
#define EVENT_A (1UL << 0)
#define EVENT_B (1UL << 1) 
// 其他模块可能意外使用相同位

// 好的做法：模块化分配
#define MODULE1_EVENT_A (1UL << 0)
#define MODULE1_EVENT_B (1UL << 1)
#define MODULE2_EVENT_A (1UL << 8)  // 从第8位开始
#define MODULE2_EVENT_B (1UL << 9)
```

## 性能优化

**减少不必要的等待**：
```c
// 不好的做法：频繁等待短超时
while(1) {
    flags = xEventGroupWaitBits(events, MASK, pdTRUE, pdFALSE, 10);
    if(flags & MASK) {
        // 处理事件
    }
}

// 好的做法：合理设置超时或使用无超时等待
flags = xEventGroupWaitBits(events, MASK, pdTRUE, pdFALSE, portMAX_DELAY);
// 或者根据业务需求设置合理超时
```

**批量处理事件**：
```c
void event_processor_task(void *pvParameters) {
    EventBits_t uxBits;
    
    while(1) {
        // 等待多个相关事件
        uxBits = xEventGroupWaitBits(xEvents, 
                                    EVENT_MASK1 | EVENT_MASK2 | EVENT_MASK3,
                                    pdFALSE, pdFALSE, portMAX_DELAY);
        
        // 批量处理所有待处理事件
        if(uxBits & EVENT_MASK1) {
            handle_event1();
            xEventGroupClearBits(xEvents, EVENT_MASK1);
        }
        if(uxBits & EVENT_MASK2) {
            handle_event2(); 
            xEventGroupClearBits(xEvents, EVENT_MASK2);
        }
        if(uxBits & EVENT_MASK3) {
            handle_event3();
            xEventGroupClearBits(xEvents, EVENT_MASK3);
        }
    }
}
```
