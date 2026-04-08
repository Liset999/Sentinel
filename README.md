# Sentinel

**轻量级 Linux 可观测性与故障诊断训练项目**  
Lightweight Linux observability and fault-diagnosis training project.

> 当前里程碑 / Current milestone: **`v0.1.1`**（第一阶段完成）

[English](#english) | [中文](#zh-cn)

---

<a id="english"></a>

## English

### What is Sentinel?
Sentinel is a **learning-oriented SRE project** designed for ByteDance SRE internship preparation. It builds observability components directly from Linux kernel interfaces (`/proc` filesystem) instead of relying on third-party libraries.

**Core focus**:
- Manual `/proc` parsing and low-level metric collection
- Prometheus Exporter
- Grafana visualization
- Fault snapshots and postmortem
- Reproducible chaos experiments (OOM / Zombie / TIME_WAIT)

### Current Status (v0.1.1)
**Stage 1 completed** – Main pipeline rebuilt from scratch (no AI-generated legacy code).

**Implemented collectors**:
- `/proc/stat` → CPU usage (two-sample calculation)
- `/proc/meminfo` → MemAvailable / MemTotal
- `/proc/loadavg` → Load Average
- `/proc/net/tcp` → TCP state counting (TIME_WAIT, CLOSE_WAIT, ESTABLISHED)
- `/proc/<pid>/stat` → Zombie process detection

**Delivered**:
- Prometheus-compatible Exporter with standard `/metrics`
- Grafana dashboard (Host Resources + Network & Processes + Exporter Health)
- Docker deployment with host `/proc` mount
- Complete deployment guide for fresh CentOS/Rocky Linux servers

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/Liset999/Sentinel.git && cd Sentinel

# 2. Start with Docker (recommended)
docker compose up -d

# 3. Verify services
# Prometheus targets: http://<your-server-ip>:9090/targets   (sentinel_monitor should be UP)
# Grafana dashboard:   http://<your-server-ip>:3000          (admin / admin)
```

### Project Layout
- `collector/` — `/proc` parsers and collectors
- `exporter/` — Prometheus Exporter
- `snapshot/` — fault snapshot scripts
- `rules/` — alert rules
- `chaos/` — fault injection scripts
- `dashboards/` — Grafana JSON
- `docs/` — notes and postmortem reports
- `tests/` — unit tests
- `Sentinel部署指南.md` — full deployment guide

### Version History
- **`v0.1.1`** (2026.04) — First stage completed: full main pipeline (collectors + exporter + Grafana + Docker)
- `v0.1.0` — Initial milestone

### 40-Day Roadmap
- **Stage 1 (Done)**: `/proc` collectors + Exporter + Grafana + Docker ✅
- **Stage 2**: OOM / Zombie / TIME_WAIT experiments + 3 postmortem reports
- **Stage 3**: Architecture & minimal K8s cognition
- **Stage 4**: Optional eBPF small POC
- **Stage 5**: Final polish for internship delivery

---

<a id="zh-cn"></a>
## 中文

### Sentinel 是什么？
Sentinel 是一个**面向字节 SRE 日常实习**的学习型项目，目标是通过**直接手写 `/proc` 解析**，完整掌握 Linux 底层可观测性与故障复盘能力。

项目严格遵循“高 ROI、低跑偏、可验收”原则，不做大而全平台，仅聚焦主链路闭环。

### 当前状态（v0.1.1）
**第一阶段已完成** —— 主链路全部从零重写，无 AI 生成痕迹。

**已实现采集模块**：
- `/proc/stat` → CPU 使用率（两次采样计算）
- `/proc/meminfo` → MemAvailable / MemTotal
- `/proc/loadavg` → 系统负载
- `/proc/net/tcp` → TCP 各状态统计（重点 TIME_WAIT）
- `/proc/<pid>/stat` → 僵尸进程统计

**已交付能力**：
- Prometheus Exporter（标准 `/metrics`）
- Grafana 监控大盘（宿主机资源、网络进程状态、采集器健康）
- Docker 标准化部署（支持宿主机 `/proc` 挂载）
- 全新服务器一键部署指南（`Sentinel部署指南.md`）

### 快速开始
```bash
# 1. 克隆项目
git clone https://github.com/Liset999/Sentinel.git && cd Sentinel

# 2. Docker 一键启动（推荐）
docker compose up -d

# 3. 验证服务
# Prometheus：http://<服务器IP>:9090/targets （sentinel_monitor 应为 UP）
# Grafana 大盘：http://<服务器IP>:3000 （默认账号密码 admin）
```

### 项目结构
- `collector/` —— `/proc` 解析器与采集器
- `exporter/` —— Prometheus 导出器
- `snapshot/` —— 故障快照脚本
- `rules/` —— 告警规则
- `chaos/` —— 故障注入脚本
- `dashboards/` —— Grafana 仪表盘
- `docs/` —— 文档与 postmortem
- `tests/` —— 单元测试
- `Sentinel部署指南.md` —— 完整部署文档

### 版本历史
- **`v0.1.1`**（2026.04）—— 第一阶段收口：主链路（采集 + Exporter + Grafana + Docker）完全跑通
- `v0.1.0` —— 初始里程碑

### 路线图（40 天计划）
- **第一阶段（已完成）**：`/proc` 采集 + Exporter + Grafana + Docker ✅
- **第二阶段**：OOM / 僵尸进程 / TIME_WAIT 三个实验 + 三份带证据 postmortem
- **第三阶段**：架构文档 + 最小 K8s 认知
- **第四阶段**：可选 eBPF 小 POC
- **第五阶段**：最终打磨为可投递、可面试版本

**项目定位**：可运行、可验证、可复盘、可脱稿讲解。不做 K8s 平台化、不做 AIOps 大杂烩，只把 SRE 最核心的主线做扎实。

