import time

#定义列表
cpu_state = [
    "cpu",
    "user",
    "nice",
    "system",
    "idle",
    "iowait",
    "irq",
    "softirq",
    "steal",
    "guest",
    "guest_nice"
]

#获取第一行
def get_cpu():
    with open("/proc/stat", "r", encoding="utf-8") as f:
        return f.readline().strip()

#将key与value对齐组成字典
def parse_cpu():
    first_line = get_cpu().split()
    cpu_dict = {}
    for i in range(0, 11):
        key = cpu_state[i]
        #非第一个字段转成整数，否则无法计算
        if i == 0:
            value = first_line[i]
        else:
            value = int(first_line[i])
        cpu_dict[key] = value
    return cpu_dict

#获得total与idle（修复后的正确逻辑）
def calculate_cpu():
    stat_cpu = parse_cpu()

    # 1. 先减掉重复统计的 guest 时间
    user = stat_cpu['user'] - stat_cpu['guest']
    nice = stat_cpu['nice'] - stat_cpu['guest_nice']

    # 2. 空闲时间只有纯 idle，不能加 iowait！
    idle = stat_cpu['idle']

    # 3. 总时间要把所有字段加全，包括 steal！
    total = (
        user + nice +
        stat_cpu['system'] +
        idle +
        stat_cpu['iowait'] +
        stat_cpu['irq'] +
        stat_cpu['softirq'] +
        stat_cpu['steal'] +
        stat_cpu['guest'] +
        stat_cpu['guest_nice']
    )
    return total, idle

#计算CPU利用率
def get_cpu_usage():
    try:
        while True:  # 别用递归，用循环，避免栈溢出
            prev_total, prev_idle = calculate_cpu()
            time.sleep(1)
            curr_total, curr_idle = calculate_cpu()

            #计算差值
            total_diff = curr_total - prev_total
            idle_diff = curr_idle - prev_idle

            if total_diff == 0:
                usage = 0.0
            else:
                # 正确的使用率：非空闲时间 / 总时间
                usage = (total_diff - idle_diff) / total_diff * 100

            print(f"CPU usage: {usage:.2f}%")

    #异常退出
    except Exception as e:
        print(e)
        return 0
    #捕获Ctrl+C
    except KeyboardInterrupt:
        print("\nStopped")
        return 0

if __name__ == "__main__":
    get_cpu_usage()

