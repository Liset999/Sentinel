from cpu import calculate_cpu, get_cpu_usage
from memory import calculate_mem
from load import parse_loadavg
from process import parse_proc
from tcp import parse_tcp

def get_all_metrics():
    metrics = {}
    #CPU
    try:
        # 先获取初始值
        prev_total, prev_idle = calculate_cpu()
        metrics["cpu"] = {"total": prev_total, "idle": prev_idle}
    except Exception as e:
        metrics["cpu"] = {"error": str(e)}
    #memory
    try:
        mem_usage = calculate_mem()
        metrics["memory"] = mem_usage
    except Exception as e:
        metrics["memory"] = {"error": str(e)}
    #load
    try:
        load_dict = parse_loadavg()
        metrics["loadavg"] = load_dict
    except Exception as e:
        metrics["loadavg"] = {"error": str(e)}
    #process
    try:
        proc_dict = parse_proc()
        metrics["proc"] = proc_dict
    except Exception as e:
        metrics["proc"] = {"error": str(e)}
    #tcp
    try:
        tcp_dict = parse_tcp()
        metrics["tcp"] = tcp_dict
    except Exception as e:
        metrics["tcp"] = {"error": str(e)}

    return metrics
if __name__ == "__main__":
    import pprint
    metrics = get_all_metrics()
    pprint.pprint(metrics)
