# Sentinel

**轻量级 Linux 可观测性与故障诊断训练项目**  
Lightweight Linux observability and fault-diagnosis training project.

> 当前里程碑 / Current milestone: **`v0.3.0`**（第一、二、三、四阶段均已完成）
<img width="2217" height="1198" alt="image" src="https://github.com/user-attachments/assets/57edf77b-e1de-442c-b0c3-c1f19b81cb55" />
<img width="2240" height="1197" alt="image" src="https://github.com/user-attachments/assets/43c979af-005c-44ae-8018-6942b929bf83" />
<img width="1553" height="907" alt="image" src="https://github.com/user-attachments/assets/230f6213-4639-4312-884c-0b48ac701876" />

<img width="2240" height="1079" alt="image" src="https://github.com/user-attachments/assets/58887204-16f7-4e9c-a173-842d4edb9c62" />



[English](#english) | [中文](#zh-cn)

---

<a id="english"></a>

## English

### What is Sentinel?
Sentinel is a **learning-oriented SRE project** built for SRE internship preparation. It collects Linux system metrics by directly parsing `/proc` filesystem files — without relying on libraries like `psutil` — and extends to eBPF-based dynamic kernel tracing.

**Core focus**:
- Manual `/proc` parsing and metric collection
- Prometheus Exporter with Alertmanager webhook integration
- Grafana visualization
- Dynamic alert threshold hot-reload via `.env`
- Fault snapshots triggered automatically on alert
- Reproducible fault experiments (OOM / Zombie / TIME_WAIT) with postmortem reports
- eBPF / bpftrace kernel probes for sub-millisecond TCP state and network tracing
- Kubernetes architecture cognition document (SRE perspective)

### Current Status (v0.3.0)

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
- Prometheus Exporter (`/metrics` endpoint, port 8000)
- Alertmanager webhook receiver (`/webhook` endpoint) — auto-triggers `snapshot.sh` on `firing` alerts
- Grafana dashboard (`grafana/dashboards/my_dashboard.json`)
- Docker Compose deployment (5 services: exporter, rule_parser sidecar, Prometheus, Grafana, Alertmanager)
- Alert rules for high memory usage, zombie processes, high TIME_WAIT, high load (`rules/default_rules.yaml`)
- Dynamic threshold engine — edit `.env` and `rules/watcher.py` reloads Prometheus rules automatically
- Fault snapshot script (`snapshot/snapshot.sh`) — captures `free`, `top`, `ps`, `ss`, kernel logs
- Unit tests for TCP, load, and process collectors (`tests/`)

#### Stage 2 — Done ✅
Fault experiments and postmortem reports completed.

**Chaos tools** (`chaos/`):
| Tool | Purpose |
|---|---|
| `memory_eater.c` | Rapidly allocates memory to trigger OOM Killer |
| `memory_eat_slow.c` | Slowly leaks memory to give monitoring time to capture the event |
| `zombie_maker.c` | Creates zombie processes |
| `short_conn_client.py` | Generates high-frequency short TCP connections to build up TIME_WAIT |

**Postmortem reports** (`docs/`):
- `postmortem-oom.md` — OOM Killer fault, Docker network namespace isolation, Pull-model race condition
- `postmortem-zombie.md` — Zombie process accumulation analysis
- `postmortem-timewait.md` — TIME_WAIT surge under short-lived connection load

#### Stage 3 — Done ✅
Architecture documentation and Kubernetes cognition document completed.

- `docs/architecture.md` — Full bilingual (EN/ZH) architecture overview with Mermaid diagrams, component responsibility table, data-flow walkthroughs, and Docker service topology
- `docs/k8s_for_sre.md` — K8s fundamentals from an SRE perspective: Pod / Deployment / Service / DaemonSet, Prometheus service discovery, breaking container isolation for host-level monitoring, and a Sentinel-to-K8s migration topology

#### Stage 4 — Done ✅
eBPF POC implemented with three bpftrace scripts.

**eBPF scripts** (`eBPF/`):
| Script | What it traces |
|---|---|
| `tcp_state.bt` | Hooks `tcp_set_state` in the kernel; prints every TCP state transition on port 8888, catching sub-millisecond connections that `/proc/net/tcp` polling always misses |
| `recv_trace.bt` | Hooks `tcp_queue_rcv` (kernel lower-half, packet enqueue) and `tcp_recvmsg` (upper-half, application dequeue) for a specific IP; reveals the two-phase receive pipeline with per-event kernel stack traces |
| `stack_trace.bt` | Hooks `__dev_queue_xmit` and captures the full kernel call stack for packets destined to a specific IP (e.g. 8.8.8.8); useful for understanding the transmit path |

**eBPF learning notes** (`docs/`):
- `ebpf_notes.md` — eBPF / BCC concepts: verifier, JIT compilation, BPF Maps, kprobes / uprobes, and why eBPF outperforms traditional polling-based observability
- `eBPF与nc对比文档.md` — Hands-on experiment: head-to-head comparison between `/proc/net/tcp` polling and eBPF event-driven tracing for capturing short-lived TCP connections; includes byte-order pitfalls for kernel struct fields

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/Liset999/Sentinel.git && cd Sentinel

# 2. (Optional) Edit alert thresholds
# vim .env   # MEM_THRESHOLD, ZOMBIE_THRESHOLD, TIME_WAIT_THRESHOLD, LOAD_THRESHOLD

# 3. Start all services with Docker Compose
docker compose up -d

# 4. Verify services
# Prometheus targets: http://<your-server-ip>:9090/targets   (sentinel_exporter should be UP)
# Grafana dashboard:  http://<your-server-ip>:3000           (admin / admin)
# Alertmanager UI:    http://<your-server-ip>:9093

# 5. Check metrics directly
curl http://localhost:8000/metrics

# 6. Run unit tests
make test

# 7. (Optional) Standalone CLI — no Docker required
python main.py

# 8. (Optional) Run an eBPF trace — requires bpftrace on the host
sudo bpftrace eBPF/tcp_state.bt
```

### Docker Compose Services
| Service | Image | Port | Role |
|---|---|---|---|
| `sentinel_exporter` | custom Python | 8000 | Metrics exporter + webhook receiver |
| `sentinel_rule_parser` | python:3.9-alpine | — | Watches `.env` & rules; hot-reloads Prometheus |
| `prometheus` | prom/prometheus | 9090 | Metrics storage and alerting engine |
| `grafana` | grafana/grafana | 3000 | Dashboard visualization |
| `alertmanager` | prom/alertmanager | 9093 | Alert routing → webhook → snapshot |

### Project Layout
```
collector/      Hand-written /proc parsers (cpu, memory, load, tcp, process) —
                the production collectors used by the exporter
exporter/       Prometheus Exporter + Alertmanager webhook (Flask app)
ai/             AI-generated reference parsers (used as a learning scaffold,
                NOT used by the exporter); covers the same metrics as collector/
                with full CPU-time breakdown, 11-state TCP mapping, and type hints
eBPF/           bpftrace scripts: tcp_state.bt, recv_trace.bt, stack_trace.bt
chaos/          Fault injection tools (OOM / zombie / TIME_WAIT)
docs/           architecture.md, k8s_for_sre.md, ebpf_notes.md,
                eBPF与nc对比文档.md, postmortem-oom.md, postmortem-zombie.md,
                postmortem-timewait.md
rules/          Alert rules (default_rules.yaml), rule_parser.py, watcher.py
grafana/        Grafana dashboard JSON and provisioning config
snapshot/       snapshot.sh — fault scene capture script
tests/          Unit tests for collectors
artifacts/      Sample snapshots and evidence files
main.py         Standalone CLI: prints live CPU / memory / load to stdout
.env            Alert threshold configuration (hot-reloadable)
```

### Alert Threshold Configuration
Thresholds are read from `.env` and applied dynamically at startup (and on every file change):
```
MEM_THRESHOLD=80          # sentinel_memory_usage > N
ZOMBIE_THRESHOLD=0        # sentinel_process_count{state="zombie"} > N
TIME_WAIT_THRESHOLD=80    # sentinel_tcp_connections{state="time_wait"} > N
LOAD_THRESHOLD=3.5        # sentinel_loadavg{interval="load5"} > N
```
`rules/watcher.py` polls `.env` and `rules/default_rules.yaml` every 5s and triggers a Prometheus hot-reload (`/-/reload`) when either file changes. No container restart is needed.

### Metric Validation
Each metric can be cross-checked with standard system commands:
- CPU: compare with `top` / `mpstat`
- Memory: compare with `free -h`
- Load: compare with `uptime`
- TCP states: compare with `ss -ant | awk '{print $1}' | sort | uniq -c`
- Zombies: compare with `ps aux | grep Z`

### CI/CD Pipeline
The repository ships a two-stage GitHub Actions workflow (`.github/workflows/ci-cd.yml`).

| Stage | Trigger | What it does |
|---|---|---|
| **CI — Unit Tests** | every push & PR to `main`/`master` | Checks out the repo, sets up Python 3.9 with pip cache, installs dependencies, runs `pytest tests/` |
| **CD — Build & Push** | push to `main`/`master` or version tag (`v*.*.*`) — **only if CI passes** | Logs in to Docker Hub, generates image tags from Git metadata, builds and pushes the `sentinel` image with registry-level layer caching |

Pull requests only trigger the CI stage (tests only); the Docker image is never pushed until the code lands on the main branch.

To enable the CD stage, add two repository secrets:
- `DOCKERHUB_USERNAME` — your Docker Hub username
- `DOCKERHUB_TOKEN` — a Docker Hub access token (not your password)

### Version History
- **`v1.0.0`** (2026.04) — First stable release: all 5 stages complete — CI/CD pipeline, final README polish, commit history, interview prep
- **`v0.3.0`** (2026.04) — Stage 3 & 4 complete: architecture doc + K8s SRE guide + eBPF bpftrace POC (3 scripts) + eBPF learning notes
- **`v0.2.0`** (2026.04) — Stage 2 complete: chaos tools + 3 postmortem reports + webhook auto-snapshot + dynamic rule hot-reload
- **`v0.1.1`** (2026.04) — Stage 1 complete: collectors + exporter + Grafana + Docker + snapshot + rules

### Roadmap
- **Stage 1 (Done)**: `/proc` collectors + Exporter + Grafana + Docker + snapshot + rules ✅
- **Stage 2 (Done)**: OOM / Zombie / TIME_WAIT experiments + 3 postmortem reports + webhook + dynamic rules ✅
- **Stage 3 (Done)**: `docs/architecture.md` + K8s SRE cognition doc ✅
- **Stage 4 (Done)**: eBPF bpftrace POC — `tcp_state.bt`, `recv_trace.bt`, `stack_trace.bt` + learning notes ✅
- **Stage 5 (Done)**: Final polish — README, CI/CD pipeline, commit history, interview prep ✅

---

<a id="zh-cn"></a>
## 中文

### Sentinel 是什么？
Sentinel 是一个**面向 SRE 日常实习**的学习型项目。核心做法是**直接解析 `/proc` 文件系统**，而不依赖 `psutil` 等第三方库，从底层掌握 Linux 可观测性；并在此基础上扩展至 **eBPF 内核动态追踪**。

项目主链路：采集 → Exporter → Grafana → 告警 → 快照 → 复盘。同时覆盖 eBPF 探针实验与 K8s SRE 认知文档。

### 当前状态（v0.3.0）

#### 第一阶段 — 已完成 ✅
主链路从零重写。

**采集模块**（全部直接读 `/proc`）：
| 数据来源 | 指标 |
|---|---|
| `/proc/stat` | CPU 使用率（两次采样差值计算） |
| `/proc/meminfo` | MemAvailable、MemTotal |
| `/proc/loadavg` | 系统负载（1 / 5 / 15 分钟） |
| `/proc/net/tcp` | TCP 状态统计：TIME_WAIT、CLOSE_WAIT、ESTABLISHED |
| `/proc/<pid>/stat` | 僵尸进程数量 |

**已交付**：
- Prometheus Exporter（`/metrics` 接口，端口 8000）
- Alertmanager Webhook 接收器（`/webhook` 接口）——`firing` 告警自动触发 `snapshot.sh`
- Grafana 监控大盘（`grafana/dashboards/my_dashboard.json`）
- Docker Compose 部署（5 个服务：exporter、rule_parser 边车、Prometheus、Grafana、Alertmanager）
- 告警规则：内存使用率过高、僵尸进程、TIME_WAIT 过高、负载过高（`rules/default_rules.yaml`）
- 动态阈值引擎——修改 `.env` 后，`rules/watcher.py` 自动热重载 Prometheus 规则
- 故障快照脚本 `snapshot/snapshot.sh`：一键抓取 `free`、`top`、`ps`、`ss`、内核日志
- 单元测试：TCP / load / process 采集器（`tests/`）

#### 第二阶段 — 已完成 ✅
故障实验与 postmortem 报告全部完成。

**混沌工程工具**（`chaos/`）：
| 工具 | 用途 |
|---|---|
| `memory_eater.c` | 快速申请内存，触发 OOM Killer |
| `memory_eat_slow.c` | 缓慢泄漏内存，给监控留出捕获窗口 |
| `zombie_maker.c` | 制造僵尸进程 |
| `short_conn_client.py` | 高频短连接，堆积 TIME_WAIT |

**Postmortem 报告**（`docs/`）：
- `postmortem-oom.md` — OOM Killer 故障、Docker 网络命名空间隔离、Pull 模型竞态条件
- `postmortem-zombie.md` — 僵尸进程积累分析
- `postmortem-timewait.md` — 短连接压测下的 TIME_WAIT 激增

#### 第三阶段 — 已完成 ✅
架构文档与 Kubernetes 认知文档全部完成。

- `docs/architecture.md` — 完整双语（中英文）架构总览：Mermaid 流程图、模块职责表、核心数据流解析、Docker 服务拓扑
- `docs/k8s_for_sre.md` — SRE 视角的 K8s 认知文档：Pod / Deployment / Service / DaemonSet 四大件、Prometheus 服务发现机制、打破容器隔离实现宿主机级监控、Sentinel 迁移 K8s 的部署拓扑设计

#### 第四阶段 — 已完成 ✅
eBPF POC 落地，三个 bpftrace 脚本均已实现。

**eBPF 脚本**（`eBPF/`）：
| 脚本 | 追踪内容 |
|---|---|
| `tcp_state.bt` | Hook 内核 `tcp_set_state`，打印 8888 端口每一次 TCP 状态跳变，能抓到 `/proc/net/tcp` 轮询必然漏掉的毫秒级短连接 |
| `recv_trace.bt` | 同时 Hook `tcp_queue_rcv`（内核下半部，入队）和 `tcp_recvmsg`（上半部，应用取件），针对特定 IP 打印内核调用栈，直观呈现两阶段接收流水线 |
| `stack_trace.bt` | Hook `__dev_queue_xmit`，抓取发往指定 IP（如 8.8.8.8）数据包的完整内核调用栈，用于理解发送路径 |

**eBPF 学习笔记**（`docs/`）：
- `ebpf_notes.md` — eBPF / BCC 核心概念：验证器（Verifier）、JIT 编译、BPF Maps、kprobes / uprobes，以及 eBPF 相比传统轮询方式在可观测性上的压倒性优势
- `eBPF与nc对比文档.md` — 动手实验复盘：`/proc/net/tcp` 轮询 vs eBPF 事件驱动在捕捉短连接上的对比；同时包含内核结构体字段字节序（主机序 vs 网络序）的避坑指南

### 快速开始
```bash
# 1. 克隆项目
git clone https://github.com/Liset999/Sentinel.git && cd Sentinel

# 2.（可选）修改告警阈值
# vim .env   # MEM_THRESHOLD、ZOMBIE_THRESHOLD、TIME_WAIT_THRESHOLD、LOAD_THRESHOLD

# 3. Docker Compose 启动全部服务
docker compose up -d

# 4. 验证服务
# Prometheus：http://<服务器IP>:9090/targets （sentinel_exporter 应为 UP）
# Grafana：   http://<服务器IP>:3000          （账号密码 admin / admin）
# Alertmanager：http://<服务器IP>:9093

# 5. 直接查看指标
curl http://localhost:8000/metrics

# 6. 运行单元测试
make test

# 7.（可选）独立 CLI，无需 Docker
python main.py

# 8.（可选）运行 eBPF 追踪——需要宿主机安装 bpftrace
sudo bpftrace eBPF/tcp_state.bt
```

### Docker Compose 服务一览
| 服务 | 镜像 | 端口 | 职责 |
|---|---|---|---|
| `sentinel_exporter` | 自定义 Python | 8000 | 指标采集 + Webhook 接收 |
| `sentinel_rule_parser` | python:3.9-alpine | — | 监听 `.env` 和规则文件，热重载 Prometheus |
| `prometheus` | prom/prometheus | 9090 | 指标存储与告警引擎 |
| `grafana` | grafana/grafana | 3000 | 可视化大盘 |
| `alertmanager` | prom/alertmanager | 9093 | 告警路由 → Webhook → 快照 |

### 项目结构
```
collector/      手写的 /proc 解析器（cpu、memory、load、tcp、process）——
                exporter 实际使用的生产级采集模块
exporter/       Prometheus Exporter + Alertmanager Webhook（Flask 应用）
ai/             AI 生成的参考版解析器（作为学习脚手架，exporter 不使用）；
                覆盖与 collector/ 相同的指标，带完整 CPU 时间分解、
                11 种 TCP 状态映射与类型注解
eBPF/           bpftrace 脚本：tcp_state.bt、recv_trace.bt、stack_trace.bt
chaos/          混沌工程工具（OOM / 僵尸进程 / TIME_WAIT）
docs/           architecture.md、k8s_for_sre.md、ebpf_notes.md、
                eBPF与nc对比文档.md、postmortem-oom.md、postmortem-zombie.md、
                postmortem-timewait.md
rules/          告警规则（default_rules.yaml）、rule_parser.py、watcher.py
grafana/        Grafana 大盘 JSON 及 provisioning 配置
snapshot/       snapshot.sh —— 故障现场快照脚本
tests/          采集器单元测试
artifacts/      样例快照与证据文件
main.py         独立 CLI：将 CPU / 内存 / 负载实时打印到终端
.env            告警阈值配置（支持热重载）
```

### 告警阈值配置
阈值在 `.env` 中定义，启动时及文件变更时自动生效：
```
MEM_THRESHOLD=80          # sentinel_memory_usage > N
ZOMBIE_THRESHOLD=0        # sentinel_process_count{state="zombie"} > N
TIME_WAIT_THRESHOLD=80    # sentinel_tcp_connections{state="time_wait"} > N
LOAD_THRESHOLD=3.5        # sentinel_loadavg{interval="load5"} > N
```
`rules/watcher.py` 每 5 秒轮询 `.env` 和 `rules/default_rules.yaml`，检测到变更后自动调用 Prometheus `/-/reload` 接口完成热重载，无需重启任何容器。

### 指标验证方式
每个指标均可用系统命令交叉验证：
- CPU：对比 `top` / `mpstat`
- 内存：对比 `free -h`
- 负载：对比 `uptime`
- TCP 状态：对比 `ss -ant | awk '{print $1}' | sort | uniq -c`
- 僵尸进程：对比 `ps aux | grep Z`

### CI/CD 流水线
项目内置两阶段 GitHub Actions 工作流（`.github/workflows/ci-cd.yml`）。

| 阶段 | 触发条件 | 执行内容 |
|---|---|---|
| **CI — 单元测试** | 向 `main`/`master` 的每次 Push 及 PR | 检出代码 → 配置 Python 3.9（含 pip 缓存）→ 安装依赖 → 运行 `pytest tests/` |
| **CD — 构建并推送镜像** | Push 到 `main`/`master` 或打版本 Tag（`v*.*.*`）——**必须 CI 通过后才执行** | 登录 Docker Hub → 从 Git 元数据自动生成镜像 Tag → 构建并推送 `sentinel` 镜像（含 Registry 层缓存） |

提 PR 时只触发 CI 阶段（只跑测试），代码合入主分支后才触发镜像推送。

启用 CD 阶段需在仓库 Settings → Secrets 中配置：
- `DOCKERHUB_USERNAME` — Docker Hub 用户名
- `DOCKERHUB_TOKEN` — Docker Hub Access Token（非密码）

### 版本历史
- **`v1.0.0`**（2026.04）—— 首个稳定版：全部五个阶段完成——CI/CD 流水线、README 最终打磨、commit 历史整理、面试准备
- **`v0.3.0`**（2026.04）—— 第三、四阶段收口：架构文档 + K8s SRE 认知指南 + eBPF bpftrace POC（3 个脚本）+ eBPF 学习笔记
- **`v0.2.0`**（2026.04）—— 第二阶段收口：混沌工具 + 三份 postmortem + Webhook 自动快照 + 动态规则热重载
- **`v0.1.1`**（2026.04）—— 第一阶段收口：采集 + Exporter + Grafana + Docker + 快照 + 告警规则

### 路线图
- **第一阶段（已完成）**：`/proc` 采集 + Exporter + Grafana + Docker + 快照脚本 + 告警规则 ✅
- **第二阶段（已完成）**：OOM / 僵尸进程 / TIME_WAIT 三个实验 + 三份带证据 postmortem + Webhook + 动态规则 ✅
- **第三阶段（已完成）**：`docs/architecture.md` + K8s SRE 认知文档 ✅
- **第四阶段（已完成）**：eBPF bpftrace POC —— `tcp_state.bt`、`recv_trace.bt`、`stack_trace.bt` + 学习笔记 ✅
- **第五阶段（已完成）**：最终打磨——README、CI/CD 流水线、commit 历史、面试准备 ✅
