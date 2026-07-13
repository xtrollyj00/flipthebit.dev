---
title: "RTL at Wire Speed #1: One Clock at a Time"
date: "2026-05-23"
tags:
  - "RTL at Wire Speed"
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
