import time

from prometheus_client import Gauge, start_http_server,Counter

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


def update_metrics():
    global _prev_cpu_times

    try:
        curr_cpu_times = parse_cpu_times(read_proc_stat())
        if _prev_cpu_times is None:
            cpu_usage.set(0.0)
        else:
            cpu_ratio = get_cpu_usage_ratio(_prev_cpu_times, curr_cpu_times)
            cpu_usage.set(cpu_ratio)
        _prev_cpu_times = curr_cpu_times
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] cpu update failed: {type(e).__name__}: {e}")
    
    try:
        memory_info = get_memory_info()
        mem_available.set(memory_info.get("MemAvailable", 0))
        mem_total.set(memory_info.get("MemTotal", 0))
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] memory update failed: {type(e).__name__}: {e}")

    try:
        load_info = get_load_average()
        load1.set(load_info.get("load1", 0.0))
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] load update failed: {type(e).__name__}: {e}") 

    try:    
        tcp_stats = get_tcp_stats()
        tcp_time_wait.set(tcp_stats.get("TIME_WAIT", 0))
        tcp_close_wait.set(tcp_stats.get("CLOSE_WAIT", 0))
        tcp_established.set(tcp_stats.get("ESTABLISHED", 0))
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] tcp update load failed: {type(e).__name__}: {e}")

    try:    
        zombie_total = count_zombie_processes()
        zombie_count.set(zombie_total)
    except Exception as e:
        exporter_update_errors.inc()
        print(f"[exporter] zombie update failed: {type(e).__name__}: {e}")
       
    exporter_last_update.set(time.time())    


if __name__ == "__main__":
    start_http_server(9090)

    while True:
        update_metrics()
        time.sleep(1)
