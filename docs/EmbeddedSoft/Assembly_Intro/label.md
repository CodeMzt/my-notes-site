## 基本概念

标签是汇编语言中的符号名称，用于标记代码或数据在内存中的位置。它代表一个地址，让程序员可以通过名称而不是硬编码的地址来引用位置。

## 语法格式

```assembly
标签名称:
    指令
```

## 标签示例

### 代码标签
```assembly
main:
    MOV R0, #10
    B   exit        @ 跳转到exit标签

loop:
    ADD R0, R0, #1
    CMP R0, #20
    BNE loop        @ 跳转回loop标签

exit:
    BX LR
```

### 数据标签
```assembly
data_area:
    .word 0x12345678    @ 定义一个字数据
    .byte 0xAA          @ 定义一个字节数据

text_string:
    .asciz "Hello"      @ 定义字符串
```

## 标签的特点

### 地址替代
```assembly
@ 编译器会将标签转换为实际地址
start:              @ 假设地址为0x08001000
    MOV R0, #1
    B   target      @ 实际编译为 B 0x08001008

target:             @ 地址0x08001008
    MOV R1, #2
```

### 作用域
- **局部标签**：通常在当前文件内可见
- **全局标签**：使用`.global`声明，对其他文件可见

```assembly
.global main        @ 声明为全局标签，链接器可见

main:
    @ 程序入口
```

## 标签的实际用途

### 流程控制
```assembly
    CMP R0, #0
    BEQ zero_case   @ 如果等于0跳转到zero_case标签
    B   non_zero    @ 否则跳转到non_zero标签

zero_case:
    MOV R1, #0
    B   end

non_zero:
    MOV R1, #1

end:
    @ 继续执行...
```

### 循环结构
```assembly
    MOV R0, #0          @ 计数器
loop_start:             @ 循环开始标签
    ADD R0, R0, #1
    CMP R0, #10
    BLT loop_start      @ 如果R0 < 10，继续循环
```

### 函数定义
```assembly
calculate_sum:          @ 函数标签
    ADD R0, R0, R1
    BX  LR

main:
    MOV R0, #5
    MOV R1, #3
    BL  calculate_sum   @ 调用函数
```

### 数据访问
```assembly
    LDR R0, =data_table @ 获取数据表地址
    LDR R1, [R0]        @ 加载第一个数据

data_table:
    .word 100, 200, 300 @ 数据定义
```

## 标签的类型

### 代码标签
标记可执行代码的位置，用于跳转和调用。

### 数据标签
标记数据存储的位置，用于加载和存储操作。

### 局部标签
某些汇编器支持数字局部标签：
```assembly
1:
    @ 代码...
    B   1b      @ 向后跳转到最近的1标签
    B   1f      @ 向前跳转到下一个1标签
1:
    @ 另一个1标签
    B   1b      @ 跳转到前一个1标签
```
## 标签的命名规则

### 有效标签名
```assembly
main:
loop1:
_data_start:
_function_123:
```

### 无效标签名
```assembly
1label:        @ 不能以数字开头
my-label:      @ 不能包含连字符
my.label:      @ 不能包含点号（除非特殊用途）
```

## 标签在反汇编中的表现

### 反汇编显示
```assembly
; 有标签的情况
0x08001000 main:
0x08001000 200A          MOVS    R0, #10
0x08001002 E002          B       exit

0x08001004 loop:
0x08001004 3001          ADDS    R0, #1

0x08001006 exit:
0x08001006 4770          BX      LR

; 无标签的情况
0x08001000 200A          MOVS    R0, #10
0x08001002 E002          B       0x08001006
0x08001004 3001          ADDS    R0, #1
0x08001006 4770          BX      LR
```

## 特殊用途标签

### 段标签
```assembly
.text                   @ 代码段开始
.global _start
_start:
    @ 代码...

.data                   @ 数据段开始
variables:
    .word 0, 0, 0

.bss                    @ 未初始化数据段
buffer:
    .space 256
```

### 对齐标签
```assembly
    .align 2            @ 4字节对齐
aligned_data:
    .word 0x12345678

    .align 3            @ 8字节对齐
double_aligned:
    .dword 0x123456789ABCDEF0
```

## 标签与地址计算

### 地址差计算
```assembly
start:
    @ 一些代码...
end:
    @ 计算代码大小
    LDR R0, =end
    LDR R1, =start
    SUB R2, R0, R1      @ R2 = 代码大小
```

### 相对地址引用
```assembly
    ADR R0, data_table  @ 获取相对地址
    LDR R1, [R0]        @ 加载数据

data_table:
    .word 0x12345678
```

## 常见标签使用模式

### 条件分支
```assembly
    CMP R0, #100
    BGT greater_than    @ 如果大于跳转
    BLT less_than       @ 如果小于跳转
    BEQ equal           @ 如果等于跳转

greater_than:
    MOV R1, #1
    B   end_compare

less_than:
    MOV R1, #-1
    B   end_compare

equal:
    MOV R1, #0

end_compare:
    @ 继续执行...
```

### 跳转表实现
```assembly
    CMP R0, #3
    BHS default_case    @ 如果>=3跳转到默认情况
    LDR PC, [PC, R0, LSL #2]  @ 跳转到对应处理程序
    B   end_switch

jump_table:
    .word case0, case1, case2

case0:
    @ 情况0处理
    B   end_switch

case1:
    @ 情况1处理
    B   end_switch

case2:
    @ 情况2处理
    B   end_switch

default_case:
    @ 默认处理

end_switch:
    @ 继续执行...
```

## 调试信息中的标签

### 带调试符号
```assembly
.LFB0:                  @ 函数开始标签
    .loc 1 10 0         @ 文件1第10行
    push    {r7, lr}
    
.LBB2:                  @ 基本块开始
    .loc 1 11 0
    movs    r0, #10
    
.LBE2:                  @ 基本块结束
    .loc 1 12 0
    pop     {r7, pc}
.LFE0:                  @ 函数结束标签
```

标签是汇编编程的基础构建块，它们使代码更易读、易维护，并提供了地址引用的抽象层。