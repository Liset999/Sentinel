# Sentinel

**轻量级 Linux 可观测性与故障诊断训练项目**  
Lightweight Linux observability and fault-diagnosis training project.

> 当前里程碑 / Current milestone: **`v0.1.1`**（第一阶段完成，第二阶段进行中）

[English](#english) | [中文](#zh-cn)

---

<a id="english"></a>

## English

### What is Sentinel?
Sentinel is a **learning-oriented SRE project** built for ByteDance SRE internship preparation. It collects Linux system metrics by directly parsing `/proc` filesystem files, without using libraries like `psutil`.

**Core focus**:
- Manual `/proc` parsing and metric collection
- Prometheus Exporter
- Grafana visualization
- Fault snapshots and postmortem reports
- Reproducible fault experiments (OOM / Zombie / TIME_WAIT)

### Current Status (v0.1.1)

#### Stage 1 — Done ✅
Main pipeline rebuilt from scratch.

**Collectors** (all read directly from `/proc`):
| Source file | Metric |
|---|---|
| `/proc/stat` | CPU usage (two-sample delta) |
| `/proc/meminfo` | MemAvailable, MemTotal |
| `/proc/loadavg` | Load average (1 / 5 / 15 min) |
| `/proc/net/tcp` | TCP state counts: TIME_WAIT, CLOSE_WAIT, ESTABLISHED |
| `/proc/<pid>/stat` | Zombie process count |

**Delivered**:
- Prometheus Exporter (`/metrics` endpoint)
- Grafana dashboard (`grafana/dashboards/my_dashboard.json`)
- Docker Compose deployment with host `/proc` mount
- Alert rules for low memory, zombie processes, high TIME_WAIT, high load (`rules/default_rules.yaml`)
- Fault snapshot script (`snapshot/snapshot.sh`) — captures `free`, `top`, `ps`, `ss`, `dmesg`
- Unit tests for TCP, load, and process collectors (`tests/`)

#### Stage 2 — In Progress 🔧
- Fault experiments (OOM / Zombie / TIME_WAIT) and postmortem reports: not yet completed

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/Liset999/Sentinel.git && cd Sentinel

# 2. Start with Docker Compose
docker compose up -d

# 3. Verify services
# Prometheus targets: http://<your-server-ip>:9090/targets   (sentinel_monitor should be UP)
# Grafana dashboard:  http://<your-server-ip>:3000           (admin / admin)

# 4. Check metrics directly
curl http://localhost:8000/metrics
```

### Project Layout
```
collector/      /proc parsers (cpu, memory, load, tcp, process)
exporter/       Prometheus Exporter (Flask app)
snapshot/       snapshot.sh — fault scene capture script
rules/          alert rules (default_rules.yaml)
grafana/        Grafana dashboard JSON and provisioning
tests/          unit tests for collectors
artifacts/      sample snapshots and evidence files
```

### Validation
Each metric can be cross-checked with standard system commands:
- CPU: compare with `top` / `mpstat`
- Memory: compare with `free -h`
- Load: compare with `uptime`
- TCP states: compare with `ss -ant | awk '{print $1}' | sort | uniq -c`
- Zombies: compare with `ps aux | grep Z`

### Version History
- **`v0.1.1`** (2026.04) — Stage 1 complete: collectors + exporter + Grafana + Docker + snapshot + rules

### Roadmap
- **Stage 1 (Done)**: `/proc` collectors + Exporter + Grafana + Docker + snapshot + rules ✅
- **Stage 2 (In progress)**: OOM / Zombie / TIME_WAIT experiments + 3 postmortem reports
- **Stage 3**: `docs/architecture.md` + minimal K8s cognition doc
- **Stage 4**: Optional eBPF small POC (only if Stage 1–3 are stable)
- **Stage 5**: Final polish — README, commit history, interview prep

---

<a id="zh-cn"></a>
## 中文

### Sentinel 是什么？
Sentinel 是一个**面向字节 SRE 日常实习**的学习型项目。核心做法是**直接解析 `/proc` 文件系统**，而不依赖 `psutil` 等第三方库，从底层掌握 Linux 可观测性。

项目只做主链路：采集 → Exporter → Grafana → 快照 → 复盘。不做 K8s 平台化，不做 AIOps。

### 当前状态（v0.1.1）

#### 第一阶段 — 已完成 ✅
主链路从零重写，无 AI 生成代码。

**采集模块**（全部直接读 `/proc`）：
| 数据来源 | 指标 |
|---|---|
| `/proc/stat` | CPU 使用率（两次采样差值计算） |
| `/proc/meminfo` | MemAvailable、MemTotal |
| `/proc/loadavg` | 系统负载（1 / 5 / 15 分钟） |
| `/proc/net/tcp` | TCP 状态统计：TIME_WAIT、CLOSE_WAIT、ESTABLISHED |
| `/proc/<pid>/stat` | 僵尸进程数量 |

**已交付**：
- Prometheus Exporter（标准 `/metrics` 接口）
- Grafana 监控大盘（`grafana/dashboards/my_dashboard.json`）
- Docker Compose 部署（挂载宿主机 `/proc`）
- 告警规则：低可用内存、僵尸进程、TIME_WAIT 过高、负载过高（`rules/default_rules.yaml`）
- 故障快照脚本 `snapshot/snapshot.sh`：一键抓取 `free`、`top`、`ps`、`ss`、`dmesg`
- 单元测试：TCP / load / process 采集器（`tests/`）

#### 第二阶段 — 进行中 🔧
- OOM / 僵尸进程 / TIME_WAIT 三个故障实验及 postmortem：尚未完成

### 快速开始
```bash
# 1. 克隆项目
git clone https://github.com/Liset999/Sentinel.git && cd Sentinel

# 2. Docker Compose 启动
docker compose up -d

# 3. 验证服务
# Prometheus：http://<服务器IP>:9090/targets （sentinel_monitor 应为 UP）
# Grafana：   http://<服务器IP>:3000          （账号密码 admin / admin）

# 4. 直接查看指标
curl http://localhost:8000/metrics
```

### 项目结构
```
collector/      /proc 解析器（cpu、memory、load、tcp、process）
exporter/       Prometheus Exporter（Flask 应用）
snapshot/       snapshot.sh —— 故障现场快照脚本
rules/          告警规则（default_rules.yaml）
grafana/        Grafana 大盘 JSON 及 provisioning 配置
tests/          采集器单元测试
artifacts/      样例快照与证据文件
```

### 指标验证方式
每个指标均可用系统命令交叉验证：
- CPU：对比 `top` / `mpstat`
- 内存：对比 `free -h`
- 负载：对比 `uptime`
- TCP 状态：对比 `ss -ant | awk '{print $1}' | sort | uniq -c`
- 僵尸进程：对比 `ps aux | grep Z`

### 版本历史
- **`v0.1.1`**（2026.04）—— 第一阶段收口：采集 + Exporter + Grafana + Docker + 快照 + 告警规则

### 路线图
- **第一阶段（已完成）**：`/proc` 采集 + Exporter + Grafana + Docker + 快照脚本 + 告警规则 ✅
- **第二阶段（进行中）**：OOM / 僵尸进程 / TIME_WAIT 三个实验 + 三份带证据 postmortem
- **第三阶段**：`docs/architecture.md` + 最小 K8s 认知文档
- **第四阶段**：可选 eBPF 小 POC（仅在前三阶段稳定后考虑）
- **第五阶段**：最终打磨——README、commit 历史、面试准备
