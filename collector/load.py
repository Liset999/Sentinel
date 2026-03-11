def read_loadavg(path="/proc/loadavg"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def parse_loadavg(text):
    parts = text.split()

    if len(parts) < 3:
        raise ValueError("invalid /proc/loadavg format")

    return {
        "load1": float(parts[0]),
        "load5": float(parts[1]),
        "load15": float(parts[2]),
    }
