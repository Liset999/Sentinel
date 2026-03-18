import time

from prometheus_client import Gauge, start_http_server, Counter

from collector.cpu import get_cpu_usage_ratio, parse_cpu_times, read_proc_stat
from collector.memory import get_memory_info
from collector.load import get_load_average
from collector.tcp import get_tcp_stats
from collector.process import count_zombie_processes

cpu_usage = Gauge("sentinel_cpu_usage_ratio", "CPU usage ratio")
mem_available = Gauge("sentinel_mem_available_kb", "Available memory in KB")
mem_total = Gauge("sentinel_mem_total_kb", "Total memory in KB")
load1 = Gauge("sentinel_load1", "1-minute load average")
tcp_time_wait = Gauge("sentinel_tcp_time_wait_count", "TCP TIME_WAIT count")
tcp_close_wait = Gauge("sentinel_tcp_close_wait_count", "TCP CLOSE_WAIT count")
tcp_established = Gauge("sentinel_tcp_established_count", "TCP ESTABLISHED count")
zombie_count = Gauge("sentinel_zombie_process_count", "Zombie process count")
exporter_last_update = Gauge(
    "sentinel_exporter_last_update_timestamp",
    "Last exporter update timestamp"
)

exporter_update_errors = Counter(
    "sentinel_exporter_update_errors_total",
    "Total exporter update errors"
)

_prev_cpu_times = None
def get_tcp_metric_value(stats, key):
    return stats.get(key, 0)

def build_metrics_snapshot():
    return {
        "cpu_usage_ratio": None,
        "mem_available_kb": None,
        "mem_total_kb": None,
        "load1": None,
        "tcp_time_wait_count": None,
        "tcp_close_wait_count": None,
        "tcp_established_count": None,
        "zombie_process_count": None,
    }

snapshot = build_metrics_snapshot()

def update_metrics():
    global _prev_cpu_times

    try:
        curr_cpu_times = parse_cpu_times(read_proc_stat())

        if _prev_cpu_times is None:
            snapshot["cpu_usage_ratio"] = 0.0
            cpu_usage.set(0.0)
        else:
            cpu_ratio = get_cpu_usage_ratio(_prev_cpu_times, curr_cpu_times)
            snapshot["cpu_usage_ratio"] = cpu_ratio
            cpu_usage.set(cpu_ratio)

        _prev_cpu_times = curr_cpu_times
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] cpu update failed: {type(e).__name__}: {e}")

    try:
        memory_info = get_memory_info()
        snapshot["mem_available_kb"] = memory_info.get("MemAvailable", 0)
        snapshot["mem_total_kb"] = memory_info.get("MemTotal", 0)

        mem_available.set(snapshot["mem_available_kb"])
        mem_total.set(snapshot["mem_total_kb"])


    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] memory update failed: {type(e).__name__}: {e}")

    try:
        load_info = get_load_average()
        snapshot["load1"] = load_info.get("load1", 0.0)
        load1.set(snapshot["load1"])
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] load update failed: {type(e).__name__}: {e}") 

    try:
        tcp_stats = get_tcp_stats()

        snapshot["tcp_time_wait_count"] = get_tcp_metric_value(tcp_stats, "TIME_WAIT")
        snapshot["tcp_close_wait_count"] = get_tcp_metric_value(tcp_stats, "CLOSE_WAIT")
        snapshot["tcp_established_count"] = get_tcp_metric_value(tcp_stats, "ESTABLISHED")

        tcp_time_wait.set(snapshot["tcp_time_wait_count"])
        tcp_close_wait.set(snapshot["tcp_close_wait_count"])
        tcp_established.set(snapshot["tcp_established_count"])
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] tcp update failed: {type(e).__name__}: {e}")

    try:    
        zombie_total = count_zombie_processes()
        snapshot["zombie_process_count"] = zombie_total
        zombie_count.set(snapshot["zombie_process_count"])
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] zombie update failed: {type(e).__name__}: {e}")
       
    exporter_last_update.set(time.time())    


if __name__ == "__main__":
    start_http_server(9090)

    while True:
        update_metrics()
        time.sleep(1)
