# exporter/app.py
import time
import subprocess
import os
from flask import Flask, request, jsonify, Response

# 🚨 CORRECTED PROMETHEUS IMPORTS 🚨
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

# 导入你的采集器
from collector.collector import get_all_metrics

class SentinelCollector:
    def collect(self):
        metrics = get_all_metrics()

        try:
            # CPU
            if "cpu" in metrics and "error" not in metrics["cpu"]:
                c_cpu = CounterMetricFamily('sentinel_cpu_jiffies_total', 'CPU jiffies', labels=['mode'])
                for mode, val in metrics["cpu"].items():
                    c_cpu.add_metric([mode], val)
                yield c_cpu

            # LoadAvg
            if "loadavg" in metrics and "error" not in metrics["loadavg"]:
                g_load = GaugeMetricFamily('sentinel_loadavg', 'System load average', labels=['interval'])
                for interval, val in metrics["loadavg"].items():
                    g_load.add_metric([interval], val)
                yield g_load

            # Memory
            if "memory" in metrics and isinstance(metrics["memory"], (float, int)):
                g_mem = GaugeMetricFamily('sentinel_memory_usage', 'Memory usage value')
                g_mem.add_metric([], metrics["memory"])
                yield g_mem

            # Process count
            if "proc" in metrics and "error" not in metrics["proc"]:
                g_proc = GaugeMetricFamily('sentinel_process_count', 'Process count by state', labels=['state'])
                for state, val in metrics["proc"].items():
                    clean_state = state.replace(" ", "_").lower()
                    g_proc.add_metric([clean_state], val)
                yield g_proc

            # TCP connections
            if "tcp" in metrics and "error" not in metrics["tcp"]:
                g_tcp = GaugeMetricFamily('sentinel_tcp_connections', 'TCP connections by state', labels=['state'])
                for state, val in metrics["tcp"].items():
                    clean_tcp_state = state.lower()
                    g_tcp.add_metric([clean_tcp_state], val)
                yield g_tcp

        except Exception as e:
            print(f"数据解析异常: {e}")

# ==================== Flask App ====================
app = Flask(__name__)

# 把 Prometheus Collector 注册到 Flask
REGISTRY.register(SentinelCollector())

# 使用 Flask 路由提供 metrics
@app.route('/metrics')
def metrics():
    """提供给 Prometheus 拉取数据的接口"""
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Alertmanager 触发告警时会 POST 到这里"""
    alert_data = request.get_json()

    print("🚨 收到 Alertmanager 告警！")
    print(alert_data)  # 打印告警内容，方便调试

    # 执行 snapshot.sh
    try:
        snapshot_path = os.path.join(os.path.dirname(__file__), "..", "snapshot", "snapshot.sh")
        result = subprocess.run(['bash', snapshot_path], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ snapshot.sh 执行成功")
            print(result.stdout)
        else:
            print(f"❌ snapshot.sh 执行失败: {result.stderr}")
    except Exception as e:
        print(f"执行 snapshot.sh 异常: {e}")

    return jsonify({"status": "success", "message": "snapshot executed"}), 200

if __name__ == '__main__':
    print("🚀 Sentinel Exporter + Webhook 已启动")
    print("   Metrics  → http://localhost:8000/metrics")
    print("   Webhook  → http://localhost:8000/webhook")
    app.run(host='0.0.0.0', port=8000, debug=False)
