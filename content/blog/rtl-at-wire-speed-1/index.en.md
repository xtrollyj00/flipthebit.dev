---
title: "RTL at Wire Speed #1: One Clock at a Time"
date: "2026-05-23"
description: "Introduction to registers, clocked logic, and RTL pipelines for FPGA beginners."
summary: "Learn how hardware executes over time by building your first RTL pipeline and verifying it with cocotb."
slug: "rtl-registers-clocked-logic-pipeline"
tags:
  - "RTL at Wire Speed"
  - rtl
  - fpga
  - vhdl
  - cocotb
  - digital-design
draft: true
---

This blog has risen from the dead! I am alive and well, finishing my master's degree and finally starting to have a bit more free time :smile:. Don't worry, the **Cache me if you can** series will continue, but it is rather academic. Honestly, I have had enough of academic writing for a while, so let me recover a bit first.

Instead, I am starting a new, more practical (but still educational) series: **RTL at Wire Speed**.

The goal of this series is to teach RTL design, intentionally not a specific RTL language, in a less traditional way. You will not spend weeks implementing another UART or SPI core that never leaves simulation. Instead, we will focus on how modern RTL systems are actually designed: streaming data, pipelines, flow control, verification, and composable hardware architectures.

The end goal is ambitious, but very real:

> go from "my eyes have never seen RTL before" to building a packet analyzer running on an actual FPGA board.

Along the way we will learn:
- how hardware really executes,
- why time is a first-class design constraint,
- how to think in pipelines instead of instructions,
- how verification should drive development,
- and how complex systems emerge from small composable blocks.

The series assumes you can already program, preferably in C or Python, but no prior FPGA or RTL knowledge is required.

## The Rhythm of Computation

*How clocks, registers, and logic bring digital systems to life*

Every CPU, GPU or ASIC is made from two simple building blocks:
- registers
- and logic.

You may know, that CPU contains set of 32 to 64 registers. But I do not mean those registers. There is huge amount of registers on a chip, like milions or billions of them. But what are they?

Every high speed circuit has a clock. CPUs use clock with a frequency in
GHz ranges. You can think of a clock as a conductor of an orchestra, where
each musical instrument and player is a piece of logic and a register can
be thought of as air storing the current sound until next beat of a 
clock (*conductor*) arrives.

Here, I will focus on semantics of each individual component of hardware.
We go deeper into how those components work, how they are implement all
the way into trasistors, but it is not the goal of this blog.

### Registers

A simple register stores a single bit for one clock cycle. It has one input
bit, usually called D, and one output bit, called Q. Registers capture and
store the input value on either the rising or falling edge of the clock signal.
Variants that capture data on both clock edges also exist, but they are
generally not available on FPGAs :smile:.

{{<
    dynamic-image
    light="img/register-light.svg"
    dark="img/register-dark.svg"
    alt="One bit register diagram."
>}}

This image shows diagram of one bit wide register. There are input (named **D**) and
output (named **Q**) wires. Also, the most important one is clock input, marked as a
triangle.

A schematic tells us how a circuit is connected, but it does not tell us how signals
change over time. Since digital hardware is fundamentally driven by time, we need 
a way to observe a circuit's behavior as time passes. The following wave diagram
shows the behavior of our one-bit register:

{{<
    dynamic-image
    light="wave/register-light.svg"
    dark="wave/register-dark.svg"
    alt="Wave diagram of one bit register behaviour."
    width="80%"
>}}

Time flows from left to right. The top trace is the clock signal, while the middle 
and bottom traces show the values of D and Q respectively. Notice that Q does not 
immediately follow D. Instead, the register samples D only on the rising edge of
the clock. Between clock edges, the output remains unchanged regardless of what happens
on the input.

At each rising edge, the current value of D is captured and appears on Q for the next
clock cycle. In this way, the register acts as a one-bit memory element, preserving
a value until the next clock edge arrives.

To implement a register in VHDL, you can write something like this:

```vhdl
process(CLK)
begin
    if rising_edge(CLK) then
        Q <= D;
    end if;
end process;
```

I left out a lot of the syntactic sugar, since you can read about that anywhere
on the internet. I'd rather focus on the semantics.

A `process` in VHDL is a behavioural description: everything inside it executes
in sequential order (VHDL has two assignment operators with different behaviours
, but that's a story for another time). This particular process is sensitive to
changes on `CLK`, meaning it re-evaluates whenever `CLK` changes. The `if rising_edge(...)`
condition then restricts execution to the rising edge of that clock. Whenever you see this
construction in VHDL, you're looking at a register.

Inside the `if`, there is a single assignment. Semantically, "assign D to Q on every clock
cycle." Once synthesized, i.e. turn from RTL to circuit, that's exactly what becomes a
register in hardware.

### Combinatorial logic

Logic by itself is very generic term. The most basic examples are operations from boolean
algebra: and, or, not, xor etc. However, more important thing is the property **combinatorial**.
Combinatorial executes instantly, without any time delay like registers.
