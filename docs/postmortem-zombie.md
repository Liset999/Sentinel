# 故障复盘报告 (Postmortem) - 僵尸进程防范与监控智能自愈演练

## 1. 基础信息

- **事件名称**：僵尸进程异常驻留与自动化快照抓取延迟事件
- **演练日期**：2026-04-12
- **报告作者**：Sentinel SRE 团队
- **事件状态**：✅ 已解决 (Resolved) & 监控体系已优化
- **影响范围**：本地混沌工程 (Chaos Engineering) 演练环境 / 无实际业务受损

## 2. 故障摘要 (Summary)

本次演练旨在验证 Sentinel 监控体系对“系统亚健康状态”的感知与取证能力。
在注入模拟缺陷程序 (`zombie_maker`) 后，系统按预期产生了 `<defunct>` 状态的僵尸进程，触发了 Prometheus 告警。但在自动化现场保留（Snapshot）环节，暴露出两个深层问题：

1. **程序级缺陷**：父进程未能正确响应内核信号回收子进程资源。
2. **监控级缺陷**：初期自动化快照未能成功抓拍到僵尸进程。根因为 Alertmanager 的 `group_interval` 机制导致的延迟，叠加 Webhook 缺乏告警状态判断（“无脑狂按快门”），导致在告警已恢复时拍摄了无效的空快照。
   最终，SRE 团队通过 `strace` 工具定位了底层死因，并通过升级 Webhook 逻辑，实现了“只看准时机智能抓拍”，完善了 SRE 故障自动闭环体系。

## 3. 详细时间线 (Timeline)

- **T0 (13:39:00)**：SRE 团队手动启动 `./chaos/zombie_maker` 进程。
- **T0+1s**：子进程 (`PID: 3185`) 打印退出信息并执行 `exit_group(0)`，变为 `<defunct>` 状态。
- **T0+15s**：Prometheus 抓取到 `sentinel_process_count{state="zombie"} == 1`，触发 `zombie_processes` 告警阈值。
- **T0+25s**：Alertmanager 经过 `group_wait` (10s) 缓冲后，向 Webhook 发出首个 `status: firing` 推送。
- **T0+26s**：**【Webhook 优化后】** Webhook 识别到现行犯 (`firing` 状态)，瞬间触发 `snapshot.sh`，成功定格包含僵尸进程的完美案发现场（13:40:52 快照）。
- **T0+60s**：`zombie_maker` 父进程休眠结束并退出。僵尸子进程被 1 号进程 (`systemd`) 收养并瞬间超度，系统僵尸数量归零。
- **T0+5m (13:44)**：Alertmanager `group_interval` (5m) 冷却期结束，发出 `status: resolved` 撤诉信。Webhook 智能识别为恢复通知，跳过快照动作，避免产生误导性垃圾数据。

## 4. 根因分析 (Root Cause Analysis / RCA)

### 4.1 产生僵尸进程的底层根因 (通过 `strace` 确证)

SRE 使用内核级系统调用追踪器（`strace -f -e trace=clone,wait4,nanosleep,exit_group`）剖析了父进程，获取到确凿的犯罪证据：

1. 父进程通过 `clone` 系统调用创建子进程 (`30887`)。
2. 子进程生命周期结束后，调用 `exit_group(0)` 释放物理资源。
3. **致命缺失**：当子进程死亡时，内核已尽责地向父进程发送了 `SIGCHLD`（死亡通知单）信号。然而，**父进程一直阻塞在** `nanosleep` **系统调用中，全程未调用** `wait4()` **进行收尸**。导致子进程的进程控制块 (PCB) 持续占用系统 PID 资源，沦为僵尸。

### 4.2 自动化快照抓拍失效的根因 (已修复)

在优化前，系统抓取了空快照（Tasks: 0 zombie），原因在于：

- 告警在 60 秒后即已恢复，但受限于 `alertmanager.yml` 中的 `group_interval: 5m` 限制，`resolved` 通知被硬生生延迟了 4 分钟发出。
- 原版 Webhook 代码（`exporter/app.py`）缺乏对 payload 中 `status` 字段的逻辑判断，导致在收到过期的恢复通知时，仍然执行了毫无意义的 `snapshot.sh`。

## 5. 解决方案与行动项 (Action Items)

| 行动项 (Action Item)                                         | 负责人   | 状态     | 预期收益                                                     |
| ------------------------------------------------------------ | -------- | -------- | ------------------------------------------------------------ |
| **[研发规范]** 修正应用程序代码，确保所有 `fork`/`clone` 出的子进程都有对应的 `wait`/`waitpid` 处理逻辑，或主动配置忽略 `SIGCHLD` 信号。 | 研发团队 | 待办     | 彻底杜绝应用层面的僵尸进程泄露。                             |
| **[监控升级]** 升级 Python Webhook 中枢（`exporter/app.py`），增加针对 `payload['status'] == 'firing'` 的严格逻辑校验。 | SRE 团队 | ✅ 已完成 | 仅在告警触发时执行快照，节省系统性能，告别“垃圾快照”，精准定位第一现场。 |
| **[工具沉淀]** 沉淀 `strace` 排障 SOP（标准操作程序），将其作为进程卡死、无故飙高、僵尸排查的标准化“法医工具”。 | SRE 团队 | ✅ 已完成 | 提升全员内核级排障能力，用数据和底层证据说话，减少跨团队推诿。 |

## 6. 经验教训 (Lessons Learned)

- **监控不能只是“狂按快门”，更要智能识别**：处理自动化应急响应时，必须基于状态机（Firing/Resolved）编写响应逻辑，而不是盲目依赖 HTTP 请求到达的时间。`group_interval` 是防风暴的必需品，Webhook 的智能判断才是最后一道防线。
- **相信底层证据，拒绝“黑盒排障”**：排查诡异的进程状态问题，直接使用 `strace` 追踪 `wait4`、`clone`、`futex` 等关键系统调用，比单纯阅读业务代码能更快、更准地锁定真凶。

------

**附录：关键现场证据快照（节选自 13:40:52 Snapshot）**

```latex
top - 13:40:52 up 3 min,  0 users,  load average: 0.16, 0.19, 0.09
Tasks: 258 total,   1 running, 256 sleeping,   0 stopped,   1 zombie
...
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 3184 root      20   0    ????   ????   ???? S   0.0   0.0   0:00.00 ./chaos/zombie_maker
 3185 root      20   0       0      0      0 Z   0.0   0.0   0:00.00 [zombie_maker] <defunct>
```

