# 介绍

空闲任务(Idle任务)的作用之一：**释放被删除的任务的内存**。

除了上述目的之外，为什么必须要有空闲任务？一个良好的程序，它的任务都是事件驱动的：平时大部分时间处于阻塞状态。有可能我们自己创建的所有任务都无法执行，但是调度器必须能找到一个可以运行的任务：所以，我们要提供空闲任务。在使用vTaskStartScheduler()函数来创建、启动调度器时，这个函数内部会创建**空闲任务**：

- 空闲任务优先级为0：它不能阻碍用户任务运行
- 空闲任务要么处于就绪态，要么处于运行态，永远不会阻塞

空闲任务的优先级为0，这意味着一旦某个用户的任务变为就绪态，那么空闲任务马上被切换出去，让这个用户任务运行。在这种情况下，我们说用户任务"抢占"(pre-empt)了空闲任务，这是由调度器实现的。

要注意的是：如果使用vTaskDelete()来删除任务，那么你就要确保空闲任务有机会执行，否则就无法释放被删除任务的内存。

我们可以添加一个空闲任务的**钩子函数(Idle Task Hook Functions)**，空闲任务的循环每执行一次，就会调用一次钩子函数。钩子函数的作用有这些：

- 执行一些低优先级的、后台的、需要连续执行的函数
- 测量系统的空闲时间：空闲任务能被执行就意味着所有的高优先级任务都停止了，所以测量空闲任务占据的时间，就可以算出处理器占用率。
- 让系统进入省电模式：空闲任务能被执行就意味着没有重要的事情要做，当然可以进入省电模式了。
- 空闲任务的钩子函数的限制：
- 不能导致空闲任务进入阻塞状态、暂停状态
- 如果你会使用vTaskDelete()来删除任务，那么**钩子函数要非常高效地执行**。如果空闲任务移植卡在钩子函数里的话，它就无法释放内存。

# 使用钩子函数

在`FreeRTOS\Source\tasks.c`中，可以看到如下代码，所以前提就是：

- 把这个宏定义为1：configUSE_IDLE_HOOK
- 实现vApplicationIdleHook函数

```c
#if ( configUSE_IDLE_HOOK == 1 )
{
    extern void vApplicationIdleHook( void );

    /* Call the user defined function from within the idle task.  This
    allows the application designer to add background functionality
    without the overhead of a separate task.
    NOTE: vApplicationIdleHook() MUST NOT, UNDER ANY CIRCUMSTANCES,
    CALL A FUNCTION THAT MIGHT BLOCK. */
    vApplicationIdleHook();
}
#endif /* configUSE_IDLE_HOOK */
```

# 调度

## 概念

这些知识在前面都提到过了，这里总结一下。

正在运行的任务，被称为"正在使用处理器"，它处于运行状态。在单处理系统中，任何时间里只能有一个任务处于运行状态。

非运行状态的任务，它处于这3中状态之一：阻塞(Blocked)、暂停(Suspended)、就绪(Ready)。就绪态的任务，可以被调度器挑选出来切换为运行状态，调度器永远都是挑选最高优先级的就绪态任务并让它进入运行状态。

阻塞状态的任务，它在等待"事件"，当事件发生时任务就会进入就绪状态。事件分为两类：**时间相关的事件、同步事件**
- **时间相关**的事件，就是设置超时时间：在指定时间内阻塞，时间到了就进入就绪状态。使用时间相关的事件，可以实现周期性的功能、可以实现超时功能。
- **同步事件**就是：某个任务在等待某些信息，别的任务或者中断服务程序会给它发送信息。怎么"发送信息"？方法很多，有：任务通知(task notification)、队列(queue)、事件组(event group)、信号量(semaphoe)、互斥量(mutex)等。这些方法用来发送同步信息，比如表示某个外设得到了数据。

## 配置调度算法

所谓调度算法，就是怎么确定哪个就绪态的任务可以切换为运行状态。

通过配置文件FreeRTOSConfig.h的两个配置项来配置调度算法：configUSE_PREEMPTION、configUSE_TIME_SLICING。

还有第三个配置项：configUSE_TICKLESS_IDLE，它是一个高级选项，用于关闭Tick中断来实现省电，后续单独讲解。现在我们假设configUSE_TICKLESS_IDLE被设为0，先不使用这个功能。 调度算法的行为主要体现在两方面：高优先级的任务先运行、同优先级的就绪态任务如何被选中。调度算法要确保同优先级的就绪态任务，能"轮流"运行，策略是"轮转调度"(Round Robin Scheduling)。轮转调度并不保证任务的运行时间是公平分配的，我们还可以细化时间的分配方法。 从3个角度统一理解多种调度算法：

- 可否抢占？高优先级的任务能否优先执行(配置项: configUSE_PREEMPTION)
    - 可以：被称作"可抢占调度"(Pre-emptive)，高优先级的就绪任务马上执行，下面再细化。
    - 不可以：不能抢就只能协商了，被称作"合作调度模式"(Co-operative Scheduling)
        - 当前任务执行时，更高优先级的任务就绪了也不能马上运行，只能等待当前任务主动让出CPU资源。
        - 其他同优先级的任务也只能等待：更高优先级的任务都不能抢占，平级的更应该老实点
- 可抢占的前提下，同优先级的任务是否轮流执行(配置项：configUSE_TIME_SLICING)
    - 轮流执行：被称为"时间片轮转"(Time Slicing)，同优先级的任务轮流执行，你执行一个时间片、我再执行一个时间片
    - 不轮流执行：英文为"without Time Slicing"，当前任务会一直执行，直到主动放弃、或者被高优先级任务抢占
- 在"可抢占"+"时间片轮转"的前提下，进一步细化：空闲任务是否让步于用户任务(配置项：configIDLE_SHOULD_YIELD)
    - 空闲任务低人一等，每执行一次循环，就看看是否主动让位给用户任务
    - 空闲任务跟用户任务一样，大家轮流执行，没有谁更特殊 列表如下：

|**配置项**|**A**|**B**|**C**|**D**|**E**|
|---|---|---|---|---|---|
|configUSE_PREEMPTION|1|1|1|1|0|
|configUSE_TIME_SLICING|1|1|0|0|x|
|configIDLE_SHOULD_YIELD|1|0|1|0|x|
|说明|常用|很少用|很少用|很少用|几乎不用|

注：

- A：可抢占+时间片轮转+空闲任务让步
- B：可抢占+时间片轮转+空闲任务不让步
- C：可抢占+非时间片轮转+空闲任务让步
- D：可抢占+非时间片轮转+空闲任务不让步
- E：合作调度

# 调度示例

## 对比效果: 抢占与否

在 **FreeRTOSConfig.h** 中，定义这样的宏，对比逻辑分析仪的效果：

```
// 实验1：抢占
##define configUSE_PREEMPTION		1
##define configUSE_TIME_SLICING      1
##define configIDLE_SHOULD_YIELD		1

// 实验2：不抢占
##define configUSE_PREEMPTION		0
##define configUSE_TIME_SLICING      1
##define configIDLE_SHOULD_YIELD		1
```

对比结果为：

- 抢占时：高优先级任务就绪时，就可以马上执行
- 不抢占时：优先级失去意义了，既然不能抢占就只能协商了，图中任务1一直在运行(一点都没有协商精神)，其他任务都无法执行。即使任务3的vTaskDelay已经超时、即使它的优先级更高，都没办法执行。

## 对比效果: 时间片轮转与否

在 **FreeRTOSConfig.h** 中，定义这样的宏，对比逻辑分析仪的效果：

```
// 实验1：时间片轮转
##define configUSE_PREEMPTION		1
##define configUSE_TIME_SLICING      1
##define configIDLE_SHOULD_YIELD		1

// 实验2：时间片不轮转
##define configUSE_PREEMPTION		1
##define configUSE_TIME_SLICING      0
##define configIDLE_SHOULD_YIELD		1
```

从下面的对比图可以知道：

- 时间片轮转：在Tick中断中会引起任务切换
- 时间片不轮转：高优先级任务就绪时会引起任务切换，高优先级任务不再运行时也会引起任务切换。可以看到任务3就绪后可以马上执行，它运行完毕后导致任务切换。其他时间没有任务切换，可以看到任务1、任务2都运行了很长时间。

## 对比效果: 空闲任务让步

在 **FreeRTOSConfig.h** 中，定义这样的宏，对比逻辑分析仪的效果：

```
// 实验1：空闲任务让步
##define configUSE_PREEMPTION		1
##define configUSE_TIME_SLICING      1
##define configIDLE_SHOULD_YIELD		1

// 实验2：空闲任务不让步
##define configUSE_PREEMPTION		1
##define configUSE_TIME_SLICING      1
##define configIDLE_SHOULD_YIELD		0
```

从下面的对比图可以知道：

- 让步时：在空闲任务的每个循环中，会主动让出处理器，从图中可以看到flagIdelTaskrun的波形很小
- 不让步时：空闲任务跟任务1、任务2同等待遇，它们的波形宽度是差不多的