# Kubernetes (K8s) 基础认知文档

**导读**：对于 SRE 而言，Kubernetes 并不是一个神秘的黑盒，而是一个高度自动化的**分布式操作系统**。在 K8s 中，我们不再直接管理物理机或进程，而是通过声明式的 API 来管理“资源”。

------

## 一、 SRE 视角的 K8s “四大件”复盘

这四个核心资源构成了 K8s 应用部署与监控的骨架：

- **Pod**：监控的最终目标实体。无论是 QPS 还是内存数据，最终都来自 Pod。
- **Deployment**：应用监控的受害者/肇事者。它会让 Pod 不断生灭、IP 不断变化，给传统静态监控带来灾难。
- **Service**：应用层监控的引路人。通过 Service 上的标签（Labels），我们可以定位背后那群不断变化的 Pod。
- **DaemonSet**：基础设施监控的锚点。无视应用层的动态漂移，死死钉在物理节点上。

### 1. Pod：K8s 中的“逻辑主机”

- **认知本质**：K8s 的最小调度单元。
- **豌豆荚模型**：不要把 Pod 简单等同于 Docker 容器。Pod 像一个“豌豆荚”，里面可以装一粒或多粒“豌豆”（容器）。
- **资源共享**：同 Pod 内的所有容器共享**网络命名空间**（同一 IP 和端口范围）和**存储卷（Volume）**。它们可通过 `localhost` 直接通信。
- **生命周期捆绑**：Pod 是生老病死的最小单位。K8s 会将整个 Pod 作为实体进行调度、销毁或重建，而不会单独拉起内部的某一个容器。

### 2. Deployment：无状态应用的“包工头”

- **认知本质**：声明式控制器与版本控制器。
- **状态维持**：Pod 是极其脆弱的（宿主机宕机、OOM 都会导致其死亡）。Deployment 负责解决这个问题，你只需声明“需要 3 个存活的副本”，它（通过底层的 **ReplicaSet**）会自动在健康节点上拉起新 Pod 来补齐数量。
- **核心功能（全生命周期管理）**：

- **平滑滚动升级（Rolling Update）**：杀一个拉一个，全程用户无感。可通过 `maxSurge` 和 `maxUnavailable` 精确控制。
- **版本回滚**：支持一键回滚到早期稳定的历史版本。
- **弹性扩缩容**：根据业务负载随时调整副本数。

### 3. Service：内部“动态注册中心 + 负载均衡器”

- **认知本质**：应对 Pod 动态 IP 的流量入口。
- **固定入口**：为一组相同功能的 Pod 提供固定的、永不改变的虚拟 IP（ClusterIP）和内部 DNS 域名。
- **流量路由**：底层由运行在每个 Node 上的 `kube-proxy` 进程负责，将 Service 信息转换为底层的包转发规则（iptables/IPVS），将流量负载均衡到存活的 Pod 上。
- **四种常见类型**：

1. `ClusterIP`：默认，仅限集群内部访问。
2. `NodePort`：映射到每个物理节点的指定端口，允许外部通过 `NodeIP:NodePort` 访问。
3. `LoadBalancer`：对接云厂商的 LB 设备。
4. `ExternalName`：将外部服务引入集群内。

### 4. DaemonSet：物理拓扑级的“保安巡逻队长”

- **认知本质**：确保每一台物理机/虚拟机（Node）上，且仅运行一个该 Pod 的副本。
- **观测场景契合度**：Deployment 关注“数量”，DaemonSet 关注“物理节点的绝对覆盖”。非常适合部署 Sentinel Agent、Node Exporter 等底层观测组件。
- **免维护的自动化**：节点伸缩（上线/下线机器）时，DaemonSet 会自动感知并在新机器上下发 Agent，或在机器移除时回收 Agent，实现 SRE 梦寐以求的省心。

------

## 二、 监控与底层观测实战

### 1. Prometheus 采集思路的进化：从“静态写死”到“情报订阅”

在 K8s 环境中，由于 Pod IP 频繁变化，静态配置 IP 的方式彻底失效。

- **服务发现 (Service Discovery)**：Prometheus 与 K8s API Server 建立连接，实时订阅带有特定标签（如 `app=sentinel-client`）的 Pod 动态 IP 列表。
- **工业级实践**：使用 **Prometheus Operator**。只需编写 `ServiceMonitor` 配置文件，声明要抓取的 Service 标签，Operator 会自动处理动态 IP 发现和配置重载。

### 2. 打破容器隔离（监控 Agent 的命门）

监控 Agent 若想拥有“上帝视角”观测宿主机状态，必须打破 Linux Namespace 的限制：

- `**hostPID: true**`**（打破进程隔离）**

- **效果**：Pod 共享宿主机 PID 命名空间，`ps -ef` 可看到宿主机全量进程（Kubelet、Docker 等）。是僵尸进程监控、资源消耗统计的前提。

- `**hostPath**`**（打破文件系统隔离）**

- **效果**：将宿主机的 `/proc`、`/sys` 挂载到容器内部（如 `/host/proc`）。Agent 读取此处的数据即为真实的物理机指标，而非容器配额。

⚠️ **安全警告**：`hostPID` 和 `hostPath` 是危险的“物理学圣剑”。黑客若攻破此类特权 Pod，可直接实现“容器逃逸”控制宿主机。生产环境中需极其严格的权限管控与审计。

------

## 三、 架构映射：Sentinel 上 K8s 的部署拓扑

如果 Sentinel 架构向 K8s 迁移，业务采集代码无需重写，只需重塑部署拓扑：

1. **采集端 (Sentinel Agent)**`**DaemonSet**`

- 自动分发到所有节点，配合 `hostPath` 挂载底层文件系统，专注本地节点指标采集。

1. **数据汇总端 (Prometheus)**`**StatefulSet**`

- 有状态副本集。保证时序数据落盘持久化，其挂载的云盘 (PVC) 会在 Pod 漂移时跟随绑定，防止数据丢失。

1. **展现与告警端 (Grafana / Alertmanager)**`**Deployment**`

- 无状态 Web 服务，多副本保证控制台高可用。

1. **内部通信**$\rightarrow$`**Service**`

- 全面抛弃硬编码 IP，组件间全部通过 K8s Service 提供的内部域名（如 `http://prometheus-service:9090`）进行互相路由与服务发现。

------

## 四、 集群大脑：etcd 存储机制

**etcd** 是一致且高可用的键值存储（Key-Value Store）系统，是 K8s 的后台数据库。

- **部署位置与角色**：非关系型数据库，通常部署在控制平面（Master 节点）。
- **存储核心数据**：K8s 中的一切资源对象（Pod 信息、Service、Endpoint 等）都会落地到 etcd。Kubernetes 1.7 之后，敏感信息（Secret）以加密形式存储。
- **单一交互入口**：etcd **只直接与 kube-apiserver 交互**。所有的增删改查操作均由 APIServer 统一写入 etcd。
- **监听与同步**：集群其他组件（如 kube-proxy、网络插件 Calico）通过监听机制感知 etcd 数据变更，实时动态修改底层规则，确保集群状态一致性。

