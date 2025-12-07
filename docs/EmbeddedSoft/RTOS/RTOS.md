# RTOS简介

与之对应的概念是裸机。RTOS全称**Real Time OS** 即**实时操作系统**。通常用于需要在严格时间限制内对外部事件做出反应的嵌入式系统，有多任务处理、调度、实时调度等功能。特点：分而治之、延时下放、抢占式、任务堆栈······
# 前置知识
见[ARM_Arch](EmbeddedSoft/ARM_Arch/ARM_Arch.md)
# 基础知识
## 任务调度
### 方式
1. **抢占式**：高的抢占低的，高优先级阻塞时（比如delay函数）会把CPU控制权下放。
2. **时间片**：同等优先级有时钟节拍负责切换任务（一个时间片为SysTick中断周期）。没有用完的时间片（中间有阻塞会直接跳过，执行不到一个时间片）直接丢弃。
3. **协程式调度**：不被抢占（已经过时）
## 任务状态
1. **运行态**
2. **就绪态**
3. **阻塞态**：控制权下放给下级就绪态
4. **挂起态**：调用`vTaskSuspend()`暂停，解除(`vTaskResume()`)后回到就绪态。
### * 任务状态列表
1. **就绪列表**：`pxReadyTasksLists[x]`，x代表优先级数目（32中为31，最低优先级保留给*空闲任务*）。同时有32位数值存储任务存在标志位。
2. **阻塞列表**：`pxDelayedTaskList`
3. **挂起列表**：`xSuspendedTaskList`
## 任务堆栈
- [Tasks_Stack](Tasks_Stack.md)
# 目录
- [任务切换](Tasks_Switch.md)
- [FreeRTOS](EmbeddedSoft/RTOS/FreeRTOS/FreeRTOS.md)