# Sentinel

Lightweight Linux observability and fault-diagnosis training project.  
轻量级 Linux 可观测性与故障诊断训练项目。

> Current milestone / 当前里程碑: `v0.1.0`

[English](#english) | [中文](#zh-cn)

---

<a id="english"></a>
## English

### What is Sentinel?

Sentinel is a learning-oriented SRE project that builds observability components directly from Linux system interfaces, especially `/proc`.

It focuses on:

- manual `/proc` parsing
- low-level system-state collection
- Prometheus-oriented metrics
- fault snapshots
- failure reproduction and debugging

### Current Status

M1 completed.

Implemented collectors / parsers:

- `/proc/stat`
- `/proc/meminfo`
- `/proc/loadavg`
- `/proc/net/tcp`
- `/proc/<pid>/stat`

Current capabilities:

- CPU stats collection
- Memory stats collection
- Load average parsing
- TCP state counting
- Zombie process counting

### Quick Start

```bash
python -m pytest -q
python collector/tcp.py
python collector/process.py
~~~

Example output:

```text
ESTABLISHED: 2
LISTEN: 1
ZOMBIE: 0
19 passed
```

### Project Layout

- `collector/` - parsers and collectors
- `exporter/` - Prometheus exporter
- `snapshot/` - fault snapshot scripts
- `rules/` - alert rules
- `chaos/` - fault injection scripts
- `dashboards/` - Grafana dashboards
- `docs/` - notes and reports
- `tests/` - unit tests

### Roadmap

- M1: `/proc` parsers and unit tests ✅
- M2: Prometheus exporter
- M3: alert rules and dashboards
- M4: chaos experiments and production-style validation

------

<a id="zh-cn"></a>
## 中文

### Sentinel 是什么？

Sentinel 是一个面向 SRE 学习与训练的项目，目标是直接基于 Linux 系统接口，尤其是 `/proc`，逐步构建可观测性组件。

当前重点包括：

- 手动解析 `/proc`
- 基于底层接口采集系统状态
- 面向 Prometheus 的指标设计
- 故障快照采集
- 常见故障复现与排查

### 当前状态

M1 已完成。

已实现的 parser / collector：

- `/proc/stat`
- `/proc/meminfo`
- `/proc/loadavg`
- `/proc/net/tcp`
- `/proc/<pid>/stat`

当前能力：

- CPU 指标采集
- 内存指标采集
- Load Average 解析
- TCP 状态统计
- 僵尸进程统计

### 快速开始

```bash
python -m pytest -q
python collector/tcp.py
python collector/process.py
```

示例输出：

```text
ESTABLISHED: 2
LISTEN: 1
ZOMBIE: 0
19 passed
```

### 项目结构

- `collector/` - 解析器与采集器
- `exporter/` - Prometheus 导出器
- `snapshot/` - 故障快照脚本
- `rules/` - 告警规则
- `chaos/` - 故障注入脚本
- `dashboards/` - Grafana 仪表盘
- `docs/` - 笔记与报告
- `tests/` - 单元测试

### 路线图

- M1：`/proc` 解析器与单元测试 ✅
- M2：Prometheus Exporter
- M3：告警规则与仪表盘
- M4：故障注入与生产式验证
