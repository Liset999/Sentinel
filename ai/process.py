import os

def parse_process_stat(content: str) -> str:
    content = content.strip()
    if not content:
        raise ValueError("empty stat content")

    right_paren = content.rfind(")")
    if right_paren == -1:
        raise ValueError("invalid stat format")

    rest = content[right_paren + 1 :].strip()
    fields = rest.split()
    if not fields:
        raise ValueError("missing process state")

    return fields[0]

def read_process_stat(pid: str, proc_root: str = "/proc") -> str:
        path = f"{proc_root}/{pid}/stat"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()



def count_zombie_processes(proc_root: str = "/proc") -> int:
    zombie_count = 0
    for entry in os.listdir(proc_root):
        if not entry.isdigit():
            continue

        try:
            content = read_process_stat(entry, proc_root)
            state = parse_process_stat(content)
        except FileNotFoundError:
            continue
        except PermissionError:
            continue
        except ValueError:
            continue

        if state == "Z":
            zombie_count += 1

    return zombie_count

if __name__ == "__main__":
    zombie_count = count_zombie_processes()
    print(f"ZOMBIE: {zombie_count}")
