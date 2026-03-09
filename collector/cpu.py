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
