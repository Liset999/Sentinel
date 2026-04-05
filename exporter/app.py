# exporter/app.py
import time
from prometheus_client import start_http_server
# 引入企业级核心神器：REGISTRY（注册表）和 MetricFamily（指标家族）
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

# 导入你的大管家
from collector.collector import get_all_metrics


class SentinelCollector:

    def collect(self):
        # 只有当有人访问 /metrics 时，这个函数才会被触发！
        # 1. 现场去抓取最新数据
        metrics = get_all_metrics()

        try:
            # --- 1. 提取 CPU (Counter) ---
            if "cpu" in metrics and "error" not in metrics["cpu"]:
                # 动态创建一个 Counter 家族，允许直接传绝对值
                c_cpu = CounterMetricFamily('sentinel_cpu_jiffies_total', 'CPU jiffies', labels=['mode'])
                for mode, val in metrics["cpu"].items():
                    c_cpu.add_metric([mode], val)
                yield c_cpu  # 交货！

            # --- 2. 提取 LoadAvg (Gauge) ---
            if "loadavg" in metrics and "error" not in metrics["loadavg"]:
                g_load = GaugeMetricFamily('sentinel_loadavg', 'System load average', labels=['interval'])
                for interval, val in metrics["loadavg"].items():
                    g_load.add_metric([interval], val)
                yield g_load

            # --- 3. 提取 Memory (Gauge) ---
            if "memory" in metrics and isinstance(metrics["memory"], (float, int)):
                g_mem = GaugeMetricFamily('sentinel_memory_usage', 'Memory usage value')
                # 单值数据不需要传标签，直接传空列表 []
                g_mem.add_metric([], metrics["memory"])
                yield g_mem

            # --- 4. 提取 proc (进程状态 Gauge) ---
            if "proc" in metrics and "error" not in metrics["proc"]:
                g_proc = GaugeMetricFamily('sentinel_process_count', 'Process count by state', labels=['state'])
                for state, val in metrics["proc"].items():
                    clean_state = state.replace(" ", "_").lower()
                    g_proc.add_metric([clean_state], val)
                yield g_proc

            # --- 5. 提取 TCP 状态 (Gauge) ---
            if "tcp" in metrics and "error" not in metrics["tcp"]:
                g_tcp = GaugeMetricFamily('sentinel_tcp_connections', 'TCP connections by state', labels=['state'])
                for state, val in metrics["tcp"].items():
                    clean_tcp_state = state.lower()
                    g_tcp.add_metric([clean_tcp_state], val)
                yield g_tcp

        except Exception as e:
            print(f"数据解析异常: {e}")


if __name__ == '__main__':
    # 2. 把我们的采集器注册到全局系统中
    REGISTRY.register(SentinelCollector())

    # 3. 开门营业
    start_http_server(8000)
    print("Sentinel Exporter (企业级按需采集版) is running on http://localhost:8000/metrics ...")

    # 4. 主线程什么都不干，只是保持程序不退出（不再有 5 秒一次的暴力死循环了）
    while True:
        time.sleep(10)
