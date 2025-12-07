[TOC]

# 原生API

## `vTaskSuspend()`

```c
void vTaskSuspend( TaskHandle_t xTaskToSuspend );
```

**参数**：

- `xTaskToSuspend`： 要挂起的任务的句柄。

## `vTaskResume()`

```c
void vTaskResume( TaskHandle_t xTaskToResume );
```

**参数**：

- `xTaskToResume`： 要恢复的任务的句柄。

> [!IMPORTANT]
>
> 在中断服务程序中使用 `vTaskResume` 是不安全的，因此 FreeRTOS 提供了一个带中断保护版本的函数。

## `xTaskResumeFromISR`

```c
BaseType_t xTaskResumeFromISR( TaskHandle_t xTaskToResume );
```

- **参数**：
  - `xTaskToResume`： 要恢复的任务的句柄。
- **返回值**：
  - `pdTRUE`： 恢复操作导致了一个更高优先级的任务就绪，并且当前中断的优先级足够低，在中断退出后应该进行一次**上下文切换**。
  - `pdFALSE`： 恢复操作不需要进行上下文切换。
- 示例

```c
	BaseType_t xYieldRequired;
    xYieldRequired = xTaskResumeFromISR( xMotorTaskHandle );
    // 如果建议进行上下文切换，并且当前中断优先级允许，则执行端口特定的切换
    if( xYieldRequired == pdTRUE ) {
        portYIELD_FROM_ISR();
    }
```

## 重要注意事项

1. **挂起计数**：

   ```c
   vTaskSuspend( xTask ); // 挂起计数 = 1
   vTaskSuspend( xTask ); // 挂起计数 = 2
   vTaskResume( xTask );  // 挂起计数 = 1 (任务仍然被挂起)
   vTaskResume( xTask );  // 挂起计数 = 0 (任务现在恢复了)
   ```

   务必确保挂起和恢复的次数匹配。

2. **c不要挂起调度器本身**： `vTaskSuspend` 挂起的是任务，而不是整个调度器。挂起所有任务会导致系统死锁。

3. **谨慎使用**： 滥用挂起/恢复可能会导致复杂的逻辑错误，比如任务依赖（A任务等待B任务的数据，但B被挂起了）导致的死锁。在设计时，通常更推荐使用**信号量、队列、事件组**等同步通信机制来协调任务，而不是简单粗暴地挂起。

4. **`vTaskSuspend(NULL)` 是唯一挂起自身的方式**： 一个任务不能通过传递自己的句柄来挂起自己，必须使用 `NULL`。

## 总结

| 特性/函数      | `vTaskSuspend`     | `vTaskResume`        | `xTaskResumeFromISR` |
| :------------- | :----------------- | :------------------- | :------------------- |
| **操作对象**   | 任务（自己或他人） | 任务（他人）         | 任务（他人）         |
| **调用上下文** | 任务               | 任务                 | **中断**             |
| **计数型**     | 是                 | 是                   | 是                   |
| **主要用途**   | 暂停一个任务的执行 | 恢复一个被挂起的任务 | 在中断中恢复任务     |

# CMSISv2 API

#### 1. 挂起线程 `osThreadSuspend()`

**函数原型**：

```
osStatus_t osThreadSuspend (osThreadId_t thread_id);
```

- **参数**：
  - `thread_id`： 要挂起的线程的线程ID（句柄）。这是一个在创建线程时获取的标识符。
- **返回值**：
  - `osOK`： 线程已被成功挂起。
  - `osErrorParameter`： 参数 `thread_id` 是 NULL 或无效。
  - `osErrorResource`： 指定的线程处于无效状态（例如已经终止）。
  - `osErrorISR`： 在中断服务程序中调用了此函数（不允许）。

**关键点**：

- 此函数可以挂起**其他线程**，也可以挂起**自己**（通过传递自己的 `thread_id`）。
- 被挂起的线程会立即停止执行，并放弃 CPU。
- 挂起是**计数型**的。如果同一个线程被多次挂起，它也需要被恢复相同的次数才能重新变为就绪状态。

#### 2. 恢复线程 `osThreadResume()`

**函数原型**：

```
osStatus_t osThreadResume (osThreadId_t thread_id);
```

- **参数**：
  - `thread_id`： 要恢复的线程的线程ID。
- **返回值**：
  - `osOK`： 线程已被成功恢复。
  - `osErrorParameter`： 参数 `thread_id` 是 NULL 或无效。
  - `osErrorResource`： 指定的线程不处于挂起状态。
  - `osErrorISR`： 在中断服务程序中调用了此函数（不允许）。

**关键点**：

- 此函数用于恢复一个被 `osThreadSuspend` 挂起的线程。
- 它会递减该线程的挂起计数。当计数减到 0 时，线程变为就绪状态，并可根据其优先级参与调度。

------

### 如何获取线程 ID？

要挂起或恢复一个线程，你必须拥有它的 `osThreadId_t`。

- **创建线程时获取**：`osThreadNew` 函数会返回线程 ID。

  ```
  osThreadId_t myThreadId = osThreadNew(thread_func, NULL, &attr);
  ```

  

- **获取自己的线程 ID**：使用 `osThreadGetId` 函数。

  ```
  osThreadId_t myOwnId = osThreadGetId();
  ```

  

- **通过线程名查找**（如果配置支持）：使用 `osThreadGetByName` 函数。

  ```
  osThreadId_t foundThreadId = osThreadGetByName("MyThreadName");
  ```