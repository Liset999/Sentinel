from __future__ import annotations

from collections import Counter
from typing import Dict


TCP_STATES = {
    "01": "ESTABLISHED",
    "02": "SYN_SENT",
    "03": "SYN_RECV",
    "04": "FIN_WAIT1",
    "05": "FIN_WAIT2",
    "06": "TIME_WAIT",
    "07": "CLOSE",
    "08": "CLOSE_WAIT",
    "09": "LAST_ACK",
    "0A": "LISTEN",
    "0B": "CLOSING",
}


def parse_tcp_table(content: str) -> Dict[str, int]:
    lines = content.splitlines()
    if not lines:
        return {}

    state_counter: Counter[str] = Counter()

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        fields = line.split()
        if len(fields) < 4:
            continue

        state_hex = fields[3].upper()
        state_name = TCP_STATES.get(state_hex, f"UNKNOWN_{state_hex}")
        state_counter[state_name] += 1

    return dict(state_counter)


def read_tcp_table(path: str = "/proc/net/tcp") -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_tcp_stats(path: str = "/proc/net/tcp") -> Dict[str, int]:
    content = read_tcp_table(path)
    return parse_tcp_table(content)


if __name__ == "__main__":
    stats = get_tcp_stats()
    for state, count in sorted(stats.items()):
        print(f"{state}: {count}")
