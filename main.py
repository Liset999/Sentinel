from collector import *
import time

try:
    # 先获取初始值
    prev_total, prev_idle = calculate_cpu()
    while True:
        time.sleep(1)  # 每秒采集一次
        cpu_usage = get_cpu_usage(prev_total, prev_idle)
        mem_usage = calculate_mem()
        print(f"CPU：{cpu_usage}%,MEM：{mem_usage}%")
        # 更新前值，为下一次计算做准备
        prev_total, prev_idle = calculate_cpu()
except KeyboardInterrupt:
    print("\n监控已退出")


