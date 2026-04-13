# Sentinel

**轻量级 Linux 可观测性与故障诊断训练项目**  
Lightweight Linux observability and fault-diagnosis training project.

> 当前里程碑 / Current milestone: **`v0.2.0`**（第一、二阶段均已完成）

[English](#english) | [中文](#zh-cn)

---

<a id="english"></a>

## English

### What is Sentinel?
Sentinel is a **learning-oriented SRE project** built for ByteDance SRE internship preparation. It collects Linux system metrics by directly parsing `/proc` filesystem files, without using libraries like `psutil`.

**Core focus**:
- Manual `/proc` parsing and metric collection
- Prometheus Exporter with Alertmanager webhook integration
- Grafana visualization
- Dynamic alert threshold hot-reload via `.env`
- Fault snapshots triggered automatically on alert
- Reproducible fault experiments (OOM / Zombie / TIME_WAIT) with postmortem reports

### Current Status (v0.2.0)

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
| `memory_eat_slow.c` | Slowly leaks memory to allow monitoring to catch the event |
| `zombie_maker.c` | Creates zombie processes |
| `short_conn_client.py` | Generates high-frequency short TCP connections to build up TIME_WAIT |

**Postmortem reports** (`docs/`):
- `postmortem-oom.md` — OOM Killer fault, Docker network namespace isolation, Pull-model race condition
- `postmortem-zombie.md` — Zombie process accumulation analysis
- `postmortem-timewait.md` — TIME_WAIT surge under short-lived connection load

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
collector/      /proc parsers (cpu, memory, load, tcp, process)
exporter/       Prometheus Exporter + Alertmanager webhook (Flask app)
ai/             Alternative /proc parsers with detailed CPU-time breakdown
chaos/          Fault injection tools (OOM / zombie / TIME_WAIT)
docs/           Postmortem reports (OOM, zombie, TIME_WAIT)
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
`rules/watcher.py` polls `.env` and `rules/default_rules.yaml` every 5s and triggers a Prometheus hot-reload (`/-/reload`) when either file changes.

### Validation
Each metric can be cross-checked with standard system commands:
- CPU: compare with `top` / `mpstat`
- Memory: compare with `free -h`
- Load: compare with `uptime`
- TCP states: compare with `ss -ant | awk '{print $1}' | sort | uniq -c`
- Zombies: compare with `ps aux | grep Z`

### Version History
- **`v0.2.0`** (2026.04) — Stage 2 complete: chaos tools + 3 postmortem reports + webhook auto-snapshot + dynamic rule hot-reload
- **`v0.1.1`** (2026.04) — Stage 1 complete: collectors + exporter + Grafana + Docker + snapshot + rules

### Roadmap
- **Stage 1 (Done)**: `/proc` collectors + Exporter + Grafana + Docker + snapshot + rules ✅
- **Stage 2 (Done)**: OOM / Zombie / TIME_WAIT experiments + 3 postmortem reports + webhook + dynamic rules ✅
- **Stage 3**: `docs/architecture.md` + minimal K8s cognition doc
- **Stage 4**: Optional eBPF small POC (only if Stage 1–3 are stable)
- **Stage 5**: Final polish — README, commit history, interview prep

---

<a id="zh-cn"></a>
## 中文

### Sentinel 是什么？
Sentinel 是一个**面向字节 SRE 日常实习**的学习型项目。核心做法是**直接解析 `/proc` 文件系统**，而不依赖 `psutil` 等第三方库，从底层掌握 Linux 可观测性。

项目只做主链路：采集 → Exporter → Grafana → 告警 → 快照 → 复盘。不做 K8s 平台化，不做 AIOps。

### 当前状态（v0.2.0）

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
collector/      /proc 解析器（cpu、memory、load、tcp、process）
exporter/       Prometheus Exporter + Alertmanager Webhook（Flask 应用）
ai/             带详细 CPU 时间分解的替代版 /proc 解析器
chaos/          混沌工程工具（OOM / 僵尸进程 / TIME_WAIT）
docs/           Postmortem 报告（OOM、僵尸进程、TIME_WAIT）
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
`rules/watcher.py` 每 5 秒轮询 `.env` 和 `rules/default_rules.yaml`，检测到变更后自动调用 Prometheus `/-/reload` 接口完成热重载。

### 指标验证方式
每个指标均可用系统命令交叉验证：
- CPU：对比 `top` / `mpstat`
- 内存：对比 `free -h`
- 负载：对比 `uptime`
- TCP 状态：对比 `ss -ant | awk '{print $1}' | sort | uniq -c`
- 僵尸进程：对比 `ps aux | grep Z`

### 版本历史
- **`v0.2.0`**（2026.04）—— 第二阶段收口：混沌工具 + 三份 postmortem + Webhook 自动快照 + 动态规则热重载
- **`v0.1.1`**（2026.04）—— 第一阶段收口：采集 + Exporter + Grafana + Docker + 快照 + 告警规则

### 路线图
- **第一阶段（已完成）**：`/proc` 采集 + Exporter + Grafana + Docker + 快照脚本 + 告警规则 ✅
- **第二阶段（已完成）**：OOM / 僵尸进程 / TIME_WAIT 三个实验 + 三份带证据 postmortem + Webhook + 动态规则 ✅
- **第三阶段**：`docs/architecture.md` + 最小 K8s 认知文档
- **第四阶段**：可选 eBPF 小 POC（仅在前三阶段稳定后考虑）
- **第五阶段**：最终打磨——README、commit 历史、面试准备
