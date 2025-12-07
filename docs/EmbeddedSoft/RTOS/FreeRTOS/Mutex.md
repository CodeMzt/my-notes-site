# 互斥量的基本概念

## 什么是互斥量

互斥量（Mutex）是用于保护共享资源的同步机制，确保在任何时刻只有一个任务可以访问临界资源。想象一下卫生间的钥匙：

- **只有一个钥匙**：同一时间只能有一个人使用卫生间
- **谁拿钥匙谁用**：拿到钥匙的人才能进入
- **用完要归还**：使用完毕后必须归还钥匙，其他人才能使用

## 互斥量的核心特性

**所有权机制**：
- 只有获取互斥量的任务才能释放它
- 系统会记录当前持有互斥量的任务

**优先级继承**：
- 当高优先级任务等待低优先级任务持有的互斥量时
- 低优先级任务会临时提升到高优先级
- 防止"优先级反转"问题

**递归访问**：
- 同一个任务可以多次获取同一个互斥量
- 需要相同次数的释放操作才能彻底释放

# 互斥量 vs 二进制信号量

## 形象对比

| 特性 | 互斥量（Mutex） | 二进制信号量（Binary Semaphore） |
|------|-----------------|----------------------------------|
| 比喻 | 卫生间钥匙 | 停车场空位信号 |
| 所有权 | 有明确所有者 | 无所有者概念 |
| 释放限制 | 只能由获取者释放 | 任何任务都可以释放 |
| 优先级处理 | 支持优先级继承 | 无优先级保护 |
| 适用场景 | 保护共享资源 | 任务同步 |

## 技术对比

```c
// 互斥量 - 用于资源保护
SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();

void vTaskAccessResource(void) {
    if(xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
        // 访问共享资源
        access_shared_resource();
        // 必须由同一个任务释放
        xSemaphoreGive(xMutex);
    }
}

// 二进制信号量 - 用于任务同步
SemaphoreHandle_t xBinarySemaphore = xSemaphoreCreateBinary();

void vProducerTask(void) {
    // 生产数据...
    xSemaphoreGive(xBinarySemaphore);  // 通知消费者
}

void vConsumerTask(void) {
    xSemaphoreTake(xBinarySemaphore, portMAX_DELAY);  // 等待生产者
    // 消费数据...
    // 不需要释放，因为用于同步
}
```

# 优先级反转问题详解

## 什么是优先级反转

优先级反转是实时系统中的经典问题，发生在不同优先级任务竞争同一资源时：

**问题场景**：
1. 低优先级任务L获取了互斥量
2. 中优先级任务M就绪，抢占了L
3. 高优先级任务H需要相同互斥量，被阻塞
4. 结果：高优先级任务H被迫等待中优先级任务M

## 互斥量的解决方案

互斥量通过**优先级继承**解决这个问题：

```c
// 没有优先级继承的情况（使用二进制信号量）
void vLowPriorityTask(void) {
    xSemaphoreTake(xBinarySemaphore, portMAX_DELAY);  // L获取信号量
    // 此时被中优先级任务M抢占
    // 高优先级任务H被阻塞，必须等待M和L都完成
    xSemaphoreGive(xBinarySemaphore);
}

// 有优先级继承的情况（使用互斥量）
void vLowPriorityTask(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);  // L获取互斥量
    // 当高优先级任务H等待时，L临时提升到H的优先级
    // L不会被M抢占，可以快速完成并释放互斥量
    xSemaphoreGive(xMutex);  // L恢复原有优先级
}
```

# FreeRTOS互斥量创建函数

## xSemaphoreCreateMutex - 创建互斥量

```c
SemaphoreHandle_t xSemaphoreCreateMutex(void);
```

**返回值**：
- 成功：互斥量句柄
- 失败：NULL（内存不足时）

**创建示例**：
```c
// 创建保护UART的互斥量
SemaphoreHandle_t xUartMutex;

void vInitMutexes(void) {
    xUartMutex = xSemaphoreCreateMutex();
    if(xUartMutex == NULL) {
        printf("ERROR: UART mutex creation failed!\n");
    } else {
        printf("UART mutex created successfully\n");
    }
}
```

## xSemaphoreCreateMutexStatic - 静态创建

```c
SemaphoreHandle_t xSemaphoreCreateMutexStatic(StaticSemaphore_t *pxMutexBuffer);
```

**参数**：
- `pxMutexBuffer`：指向静态分配的内存块

**静态创建示例**：
```c
// 静态分配互斥量内存
static StaticSemaphore_t xUartMutexBuffer;

void vInitStaticMutex(void) {
    xUartMutex = xSemaphoreCreateMutexStatic(&xUartMutexBuffer);
}
```

## xSemaphoreCreateRecursiveMutex - 创建递归互斥量

```c
SemaphoreHandle_t xSemaphoreCreateRecursiveMutex(void);
```

**递归互斥量特点**：
- 同一个任务可以多次获取
- 需要相同次数的释放操作
- 防止自死锁

# 互斥量操作函数

## xSemaphoreTake - 获取互斥量

```c
BaseType_t xSemaphoreTake(SemaphoreHandle_t xSemaphore, 
                         TickType_t xTicksToWait);
```

**参数**：
- `xSemaphore`：互斥量句柄
- `xTicksToWait`：等待超时时间

**返回值**：
- `pdTRUE`：成功获取互斥量
- `pdFALSE`：超时未获取到

**使用模式**：
```c
if(xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
    // 进入临界区，访问共享资源
    access_shared_resource();
    
    // 退出临界区
    xSemaphoreGive(xMutex);
} else {
    // 处理获取失败的情况
    handle_mutex_timeout();
}
```

## xSemaphoreGive - 释放互斥量

```c
BaseType_t xSemaphoreGive(SemaphoreHandle_t xSemaphore);
```

**重要规则**：
- **必须由获取互斥量的任务释放**
- 不能在中断服务程序中使用
- 递归互斥量需要匹配的释放次数

## 递归互斥量操作

### xSemaphoreTakeRecursive
```c
BaseType_t xSemaphoreTakeRecursive(SemaphoreHandle_t xMutex,
                                  TickType_t xTicksToWait);
```

### xSemaphoreGiveRecursive
```c
BaseType_t xSemaphoreGiveRecursive(SemaphoreHandle_t xMutex);
```

**递归互斥量使用示例**：
```c
void vComplexOperation(void) {
    // 第一次获取
    if(xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY) == pdTRUE) {
        // 调用其他可能也需要同一互斥量的函数
        vSubFunction();
        
        // 需要匹配的释放次数
        xSemaphoreGiveRecursive(xRecursiveMutex);
    }
}

void vSubFunction(void) {
    // 第二次获取（同一个任务）
    if(xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY) == pdTRUE) {
        // 执行操作...
        xSemaphoreGiveRecursive(xRecursiveMutex);
    }
}
```

# 互斥量删除函数

## vSemaphoreDelete - 删除互斥量

```c
void vSemaphoreDelete(SemaphoreHandle_t xSemaphore);
```

**使用注意事项**：
- 确保没有任务正在等待或持有互斥量
- 动态创建的互斥量才会释放内存
- 静态创建的互斥量只重置状态，不释放内存

**删除示例**：
```c
void vCleanupMutexes(void) {
    // 检查是否有任务持有互斥量
    if(uxSemaphoreGetCount(xUartMutex) == 0) {
        vSemaphoreDelete(xUartMutex);
        xUartMutex = NULL;
        printf("UART mutex deleted\n");
    } else {
        printf("Warning: Cannot delete mutex, it's currently held\n");
    }
}
```

# 互斥量查询函数

## uxSemaphoreGetCount - 获取信号量计数

```c
UBaseType_t uxSemaphoreGetCount(SemaphoreHandle_t xSemaphore);
```

**对于互斥量的返回值**：
- 1：互斥量可用
- 0：互斥量已被占用

**使用示例**：
```c
void vCheckMutexStatus(void) {
    UBaseType_t uxCount = uxSemaphoreGetCount(xUartMutex);
    
    if(uxCount == 1) {
        printf("Mutex is available\n");
    } else {
        printf("Mutex is currently held by another task\n");
    }
}
```

# 互斥量综合实验案例：多任务共享资源保护

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "stdio.h"
#include "string.h"

// 共享资源 - 全局数据
typedef struct {
    int temperature;
    int humidity;
    int pressure;
    uint32_t update_count;
} SharedSensorData_t;

// 共享资源实例
static SharedSensorData_t xSharedData = {0};

// 互斥量句柄
SemaphoreHandle_t xDataMutex;        // 保护共享数据
SemaphoreHandle_t xDisplayMutex;     // 保护显示输出
SemaphoreHandle_t xFileMutex;        // 保护文件操作

// 传感器数据采集任务
void vSensorTask(void *pvParameters) {
    int task_id = (int)pvParameters;
    int local_temp, local_humid, local_press;
    
    printf("Sensor Task %d started\n", task_id);
    
    while(1) {
        // 模拟传感器读数
        local_temp = 20 + task_id + (rand() % 5);
        local_humid = 40 + task_id * 5 + (rand() % 10);
        local_press = 1000 + task_id * 10 + (rand() % 20);
        
        // 获取数据互斥量
        if(xSemaphoreTake(xDataMutex, 100 / portTICK_PERIOD_MS) == pdTRUE) {
            // 更新共享数据
            xSharedData.temperature = local_temp;
            xSharedData.humidity = local_humid;
            xSharedData.pressure = local_press;
            xSharedData.update_count++;
            
            printf("Sensor%d updated shared data (count: %lu)\n", 
                   task_id, xSharedData.update_count);
            
            // 释放互斥量
            xSemaphoreGive(xDataMutex);
        } else {
            printf("Sensor%d: Failed to get data mutex!\n", task_id);
        }
        
        vTaskDelay(2000 / portTICK_PERIOD_MS);
    }
}

// 数据显示任务
void vDisplayTask(void *pvParameters) {
    SharedSensorData_t display_data;
    
    printf("Display Task started\n");
    
    while(1) {
        // 获取数据互斥量读取数据
        if(xSemaphoreTake(xDataMutex, portMAX_DELAY) == pdTRUE) {
            // 拷贝数据到局部变量
            memcpy(&display_data, &xSharedData, sizeof(SharedSensorData_t));
            xSemaphoreGive(xDataMutex);
            
            // 获取显示互斥量进行输出
            if(xSemaphoreTake(xDisplayMutex, 50 / portTICK_PERIOD_MS) == pdTRUE) {
                printf("\n=== Current Sensor Readings ===\n");
                printf("Temperature: %d°C\n", display_data.temperature);
                printf("Humidity:    %d%%\n", display_data.humidity);
                printf("Pressure:    %dhPa\n", display_data.pressure);
                printf("Update Count: %lu\n", display_data.update_count);
                printf("===============================\n");
                
                xSemaphoreGive(xDisplayMutex);
            }
        }
        
        vTaskDelay(3000 / portTICK_PERIOD_MS);
    }
}

// 数据记录任务（模拟文件操作）
void vDataLoggerTask(void *pvParameters) {
    SharedSensorData_t log_data;
    static uint32_t log_count = 0;
    
    printf("Data Logger Task started\n");
    
    while(1) {
        // 获取数据互斥量
        if(xSemaphoreTake(xDataMutex, portMAX_DELAY) == pdTRUE) {
            memcpy(&log_data, &xSharedData, sizeof(SharedSensorData_t));
            xSemaphoreGive(xDataMutex);
            
            // 获取文件互斥量（模拟文件操作）
            if(xSemaphoreTake(xFileMutex, 100 / portTICK_PERIOD_MS) == pdTRUE) {
                // 模拟文件写入操作
                printf("Log[%lu]: Writing data to file...\n", ++log_count);
                vTaskDelay(100 / portTICK_PERIOD_MS);  // 模拟写入时间
                printf("Log[%lu]: Data written successfully\n", log_count);
                
                xSemaphoreGive(xFileMutex);
            } else {
                printf("Logger: File busy, skipping log entry\n");
            }
        }
        
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}

// 系统监控任务
void vSystemMonitorTask(void *pvParameters) {
    printf("System Monitor Task started\n");
    
    while(1) {
        // 检查各个互斥量状态
        UBaseType_t data_status = uxSemaphoreGetCount(xDataMutex);
        UBaseType_t display_status = uxSemaphoreGetCount(xDisplayMutex);
        UBaseType_t file_status = uxSemaphoreGetCount(xFileMutex);
        
        printf("\n--- System Monitor ---\n");
        printf("Data Mutex:    %s\n", data_status ? "Available" : "In Use");
        printf("Display Mutex: %s\n", display_status ? "Available" : "In Use");
        printf("File Mutex:    %s\n", file_status ? "Available" : "In Use");
        printf("Shared Data Update Count: %lu\n", xSharedData.update_count);
        
        vTaskDelay(10000 / portTICK_PERIOD_MS);
    }
}

// 递归互斥量演示任务
void vRecursiveMutexDemoTask(void *pvParameters) {
    SemaphoreHandle_t xRecursiveMutex = xSemaphoreCreateRecursiveMutex();
    
    printf("Recursive Mutex Demo Task started\n");
    
    while(1) {
        // 第一次获取递归互斥量
        if(xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY) == pdTRUE) {
            printf("Recursive: First take\n");
            
            // 第二次获取（同一个任务）
            if(xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY) == pdTRUE) {
                printf("Recursive: Second take\n");
                
                // 执行一些操作
                vTaskDelay(100 / portTICK_PERIOD_MS);
                
                // 第一次释放
                xSemaphoreGiveRecursive(xRecursiveMutex);
                printf("Recursive: First give\n");
            }
            
            // 第二次释放
            xSemaphoreGiveRecursive(xRecursiveMutex);
            printf("Recursive: Second give - fully released\n");
        }
        
        vTaskDelay(8000 / portTICK_PERIOD_MS);
    }
}

// 优先级反转演示任务
void vPriorityInversionDemoTask(void *pvParameters) {
    int task_id = (int)pvParameters;
    
    printf("Priority Demo Task %d started\n", task_id);
    
    while(1) {
        if(task_id == 1) {  // 低优先级任务
            printf("LowPriority: Trying to get mutex\n");
            if(xSemaphoreTake(xDataMutex, portMAX_DELAY) == pdTRUE) {
                printf("LowPriority: Got mutex, working...\n");
                vTaskDelay(3000 / portTICK_PERIOD_MS);  // 长时间占用
                printf("LowPriority: Releasing mutex\n");
                xSemaphoreGive(xDataMutex);
            }
            vTaskDelay(10000 / portTICK_PERIOD_MS);
            
        } else if(task_id == 3) {  // 高优先级任务
            vTaskDelay(1000 / portTICK_PERIOD_MS);  // 让低优先级先运行
            printf("HighPriority: Trying to get mutex\n");
            TickType_t start_time = xTaskGetTickCount();
            
            if(xSemaphoreTake(xDataMutex, portMAX_DELAY) == pdTRUE) {
                TickType_t end_time = xTaskGetTickCount();
                printf("HighPriority: Got mutex after %lu ms\n", 
                       (end_time - start_time) * portTICK_PERIOD_MS);
                xSemaphoreGive(xDataMutex);
            }
            vTaskDelay(15000 / portTICK_PERIOD_MS);
        }
    }
}

// 系统初始化
void vInitMutexSystem(void) {
    // 创建所有互斥量
    xDataMutex = xSemaphoreCreateMutex();
    xDisplayMutex = xSemaphoreCreateMutex();
    xFileMutex = xSemaphoreCreateMutex();
    
    if(xDataMutex == NULL || xDisplayMutex == NULL || xFileMutex == NULL) {
        printf("ERROR: Mutex creation failed!\n");
        while(1);
    }
    
    printf("All mutexes created successfully\n");
}

// 主函数
int main(void) {
    printf("Starting Mutex Demonstration System...\n");
    
    // 初始化互斥量系统
    vInitMutexSystem();
    
    // 创建传感器任务（3个）
    xTaskCreate(vSensorTask, "Sensor1", 1024, (void*)1, 1, NULL);
    xTaskCreate(vSensorTask, "Sensor2", 1024, (void*)2, 1, NULL);
    xTaskCreate(vSensorTask, "Sensor3", 1024, (void*)3, 1, NULL);
    
    // 创建处理任务
    xTaskCreate(vDisplayTask, "Display", 1024, NULL, 2, NULL);
    xTaskCreate(vDataLoggerTask, "Logger", 1024, NULL, 2, NULL);
    xTaskCreate(vSystemMonitorTask, "Monitor", 1024, NULL, 1, NULL);
    xTaskCreate(vRecursiveMutexDemoTask, "Recursive", 1024, NULL, 1, NULL);
    
    // 创建优先级演示任务
    xTaskCreate(vPriorityInversionDemoTask, "LowPriority", 1024, (void*)1, 1, NULL);
    xTaskCreate(vPriorityInversionDemoTask, "MidPriority", 1024, (void*)2, 2, NULL);
    xTaskCreate(vPriorityInversionDemoTask, "HighPriority", 1024, (void*)3, 3, NULL);
    
    // 启动调度器
    printf("Starting FreeRTOS scheduler...\n");
    vTaskStartScheduler();
    
    return 0;
}
```

# 互斥量使用最佳实践

## 设计原则

**保持临界区简短**：
```c
// 好的做法：只保护共享数据访问
if(xSemaphoreTake(xMutex, timeout) == pdTRUE) {
    // 快速操作：只拷贝数据或更新变量
    shared_variable = new_value;
    xSemaphoreGive(xMutex);
}
// 耗时操作放在临界区外
process_data(shared_variable);

// 不好做法：在临界区内执行耗时操作
if(xSemaphoreTake(xMutex, timeout) == pdTRUE) {
    // 这会长时间阻塞其他任务
    long_processing_operation();
    xSemaphoreGive(xMutex);
}
```

**避免嵌套死锁**：
```c
// 危险：可能产生死锁
void vFunctionA(void) {
    xSemaphoreTake(xMutex1, portMAX_DELAY);
    xSemaphoreTake(xMutex2, portMAX_DELAY);  // 如果其他任务以相反顺序获取，会产生死锁
    // ...
    xSemaphoreGive(xMutex2);
    xSemaphoreGive(xMutex1);
}

// 安全：固定获取顺序
void vFunctionA(void) {
    xSemaphoreTake(xMutex1, portMAX_DELAY);
    xSemaphoreTake(xMutex2, portMAX_DELAY);
    // ...
    xSemaphoreGive(xMutex2);
    xSemaphoreGive(xMutex1);
}

void vFunctionB(void) {
    xSemaphoreTake(xMutex1, portMAX_DELAY);  // 同样顺序
    xSemaphoreTake(xMutex2, portMAX_DELAY);
    // ...
    xSemaphoreGive(xMutex2);
    xSemaphoreGive(xMutex1);
}
```

## 错误处理策略

**超时处理**：
```c
BaseType_t xResult = xSemaphoreTake(xMutex, reasonable_timeout);
if(xResult != pdTRUE) {
    // 处理策略：
    // 1. 使用默认值继续执行
    // 2. 跳过本次操作
    // 3. 尝试恢复或重置系统
    handle_mutex_timeout();
    return;
}
```

**资源清理**：
```c
void vCriticalOperation(void) {
    if(xSemaphoreTake(xMutex, timeout) == pdTRUE) {
        // 确保在任何退出路径都释放互斥量
        if(operation_failed) {
            xSemaphoreGive(xMutex);
            return;
        }
        
        // 正常操作...
        xSemaphoreGive(xMutex);
    }
}
```

