import time

cpu_state = (
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
    )

# 获取/proc/stat第一行CPU数据
def get_cpu(file_path="/proc/stat"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readline().strip()

# 键名与数值对齐，解析为正确字典
def parse_cpu():
    first_line = get_cpu().split()
    cpu_nums = list(map(int, first_line[1:]))  # 切掉表头"cpu"，保留数字部分
    cpu_dict = dict(zip(cpu_state, cpu_nums))  # 现在键名和数值完全匹配
    return cpu_dict

# 计算total和idle
def calculate_cpu():
    stat_cpu = parse_cpu()

    # 1. 减掉重复统计的 guest 时间
    user = stat_cpu['user'] - stat_cpu['guest']
    nice = stat_cpu['nice'] - stat_cpu['guest_nice']

    # 2. 空闲时间只有纯 idle
    idle = stat_cpu['idle']

    # 3. 总时间包含所有字段
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

# 清理冗余代码，仅负责计算CPU使用率
def get_cpu_usage(prev_total, prev_idle):
    curr_total, curr_idle = calculate_cpu()
    # 计算差值
    total_diff = curr_total - prev_total
    idle_diff = curr_idle - prev_idle

    if total_diff == 0:
        return 0.0
    # 正确的使用率：非空闲时间 / 总时间
    usage = (total_diff - idle_diff) / total_diff * 100
    return round(usage, 2)  # 保留2位小数，更易读

# 主循环：实现每秒打印CPU使用率，捕获Ctrl+C
if __name__ == "__main__":
    print("开始监控CPU使用率（按Ctrl+C退出）...")
    try:
        # 先获取初始值
        prev_total, prev_idle = calculate_cpu()
        while True:
            time.sleep(1)  # 每秒采集一次
            cpu_usage = get_cpu_usage(prev_total, prev_idle)
            print(f"当前CPU使用率：{cpu_usage}%")
            # 更新前值，为下一次计算做准备
            prev_total, prev_idle = calculate_cpu()
    except KeyboardInterrupt:
        print("\n监控已退出")
