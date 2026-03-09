def read_proc_stat(path="/proc/stat"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_cpu_times(stat_text):
    first_line = stat_text.splitlines()[0].strip()
    parts = first_line.split()

    if parts[0] != "cpu":
        raise ValueError("first line is not cpu")

    return {
        "user": int(parts[1]),
        "nice": int(parts[2]),
        "system": int(parts[3]),
        "idle": int(parts[4]),
        "iowait": int(parts[5]),
        "irq": int(parts[6]),
        "softirq": int(parts[7]),
        "steal": int(parts[8]),
    }
 

def get_total_and_idle(cpu_times):
    total = (
        cpu_times["user"]
        + cpu_times["nice"]
        + cpu_times["system"]
        + cpu_times["idle"]
        + cpu_times["iowait"]
        + cpu_times["irq"]
        + cpu_times["softirq"]
        + cpu_times["steal"]
    )
    idle = cpu_times["idle"] + cpu_times["iowait"]
    return total,idle

def calculate_cpu_usage(prev_cpu_times,curr_cpu_times):
    prev_total, prev_idle = get_total_and_idle(prev_cpu_times)
    curr_total, curr_idle = get_total_and_idle(curr_cpu_times)

    total_delta = curr_total - prev_total
    idle_delta = curr_idle - prev_idle

    if total_delta <= 0:
        return 0.0

    return (total_delta - idle_delta) / total_delta * 100
