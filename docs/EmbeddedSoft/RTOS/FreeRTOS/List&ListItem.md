[TOC]

# FreeRTOS 列表和列表项的用途

## 内核调度管理

### 就绪列表 (Ready Lists)

每个优先级都有一个独立的就绪列表，用于管理处于就绪状态的任务。调度器通过遍历这些列表来选择最高优先级的就绪任务运行。

### 延迟列表 (Delayed List)

管理被延迟的任务，按唤醒时间排序。当系统时钟滴答发生时，检查并移动到期任务到就绪列表。

### 挂起列表 (Pending Ready List)

在调度器挂起期间变为就绪的任务临时存放在此列表，待调度器恢复时再转移到就绪列表。

### 事件列表

用于管理等待事件（如信号量、队列、事件组）的任务，按优先级排序。

## 资源管理

### 任务状态跟踪

通过列表管理任务的不同状态转换，确保任务在适当的时候被调度执行。

### 定时器管理

软件定时器使用列表来管理定时器的触发时间和执行顺序。

### 内存管理

某些内存分配方案使用列表来跟踪空闲内存块。

# 列表和列表项的概念

列表是 FreeRTOS 内核中的基础数据结构，用于管理任务和各种内核对象。所有列表都实现为**双向环形链表**，确保高效的插入和删除操作。

## 列表 (List)
列表是 FreeRTOS 中用于组织和管理多个相关项目的数据结构。每个列表包含头尾指针和项目计数，主要用于：
- 就绪任务列表
- 延迟任务列表
- 挂起任务列表
- 事件等待列表

## 列表项 (ListItem)
列表项是列表中的基本元素，每个列表项包含前后指针和所属列表指针。列表项还包含一个排序值，用于在列表中按升序排列。

# 列表结构体定义

## List_t 结构体
```c
typedef struct xLIST
{
    listFIRST_LIST_INTEGRITY_CHECK_VALUE
    volatile UBaseType_t uxNumberOfItems;
    ListItem_t * configLIST_VOLATILE pxIndex;
    MiniListItem_t xListEnd;
    listSECOND_LIST_INTEGRITY_CHECK_VALUE
} List_t;
```

**成员说明：**
- `uxNumberOfItems`：记录列表中列表项的数量，不含 `xListEnd`
- `pxIndex`：用于遍历列表的指针，指向当前被引用的列表项
- `xListEnd`：列表尾标记，是一个迷你列表项
- `listFIRST_LIST_INTEGRITY_CHECK_VALUE`：这两个宏是确定的已知常量，FreeRTOS通过检查这两个常量的值，来判断列表的数据在程序运行的过程中，是否遭到破坏，该功能一般用于调试，默认不开启。

## ListItem_t 结构体
```c
struct xLIST_ITEM
{
    listFIRST_LIST_ITEM_INTEGRITY_CHECK_VALUE
    configLIST_VOLATILE TickType_t xItemValue;
    struct xLIST_ITEM * configLIST_VOLATILE pxNext;
    struct xLIST_ITEM * configLIST_VOLATILE pxPrevious;
    void * pvOwner;
    struct xLIST * configLIST_VOLATILE pxContainer;
    listSECOND_LIST_ITEM_INTEGRITY_CHECK_VALUE
};
```

**成员说明：**
- `xItemValue`：排序值，用于确定列表项在列表中的位置，为0xFFFFFFFF(32位)
- `pxNext`：指向下一个列表项的指针
- `pxPrevious`：指向前一个列表项的指针
- `pvOwner`：指向拥有该列表项的对象（通常是任务控制块）
- `pxContainer`：指向该列表项所属的列表

## MiniListItem_t 结构体
```c
typedef struct xMINI_LIST_ITEM
{
    listFIRST_LIST_ITEM_INTEGRITY_CHECK_VALUE
    configLIST_VOLATILE TickType_t xItemValue;
    struct xLIST_ITEM * configLIST_VOLATILE pxNext;
    struct xLIST_ITEM * configLIST_VOLATILE pxPrevious;
} MiniListItem_t;
```
迷你列表项是简化版的列表项，主要用于列表尾标记以及挂载其他插入列表中的列表项，不包含所有者指针和容器指针。	

### 用处

当列表为空时，我们怎么加入新项？这时候就需要这个Mini列表项，用来挂载加入列表的新元素。当列表为空时，它的两只手（Previous和Next）都指向自己。

# 列表操作 API

## 列表初始化
- `vListInitialise(List_t* const pxList)` - 初始化列表
- `vListInitialiseItem(ListItem_t* const pxItem)` - 初始化列表项

## 列表项操作
- `vListInsert(List_t* const pxList, ListItem_t* const pxNewListItem)` - 按排序值插入列表项
- `vListInsertEnd(List_t* const pxList, ListItem_t* const pxNewListItem)` - 在列表中当前指向列表项前插入，即插入已遍历的最末端，是一种无序插入方法。
- `uxListRemove(ListItem_t* const pxItemToRemove)` - 从列表中移除列表项

## 列表遍历
- `listGET_OWNER_OF_NEXT_ENTRY()` - 获取下一个列表项的所有者
- `listLIST_IS_EMPTY()` - 检查列表是否为空

# 列表的特点

## 排序机制
列表项按 xItemValue 值升序排列，这对于时间相关的操作（如任务延迟）非常有用。

## 完整性检查
当 configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES 设置为 1 时，列表和列表项会包含完整性检查字节，用于检测内存损坏。

## 线程安全
列表操作不是原子性的，在操作列表时需要挂起调度器或使用关键段来保证线程安全。