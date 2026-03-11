def read_meminfo(path="/proc/meminfo"):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def parse_meminfo(lines):
    result = {}

    for line in lines:
        parts = line.split()

        if len(parts) < 2:
            continue

        key = parts[0].rstrip(":")
        value = int(parts[1])

        result[key] = value

    return result


def get_memory_usage_percent(path="/proc/meminfo"):
    lines = read_meminfo(path)
    data = parse_meminfo(lines)

    total = data.get("MemTotal", 0)
    available = data.get("MemAvailable", 0)

    if total == 0:
        return 0.0

    return (total - available) / total * 100
