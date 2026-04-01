import os

# 进程状态映射字典
process_state = {
    'R': 'Running',
    'S': 'Interruptible Sleep',
    'D': 'Uninterruptible Disk Sleep',
    'Z': 'Zombie',
    'T': 'Stopped(by signal)',
    't': 'Tracing Stop'
}

def list_proc(proc_dir='/proc'):
    """获取所有数字PID目录"""
    lines = os.listdir(proc_dir)
    pids = []
    for proc in lines:
        if proc.isdigit():
            pids.append(proc)
    return pids

def parse_proc(proc_dir='/proc'):
    """解析进程状态并统计"""
    pids = list_proc(proc_dir)
    metrics = {state: 0 for state in process_state.values()}

    # 遍历所有PID
    for pid in pids:
        try:
            # 拼接文件路径
            file_path = os.path.join(proc_dir, pid, 'stat')
            with open(file_path, 'r', encoding='utf-8') as f:
                # ✅ 关键修复：这里必须缩进！！
                content = f.read()
                # 找到最后一个右括号
                right_paren = content.rfind(')')
                # 提取状态字符
                status = content[right_paren + 2]

                # 统计数量
                if status in process_state:
                    metrics[process_state[status]] += 1

        # 进程退出，忽略错误
        except FileNotFoundError:
            continue

    return metrics

if __name__ == '__main__':
    # 直接运行查看系统进程状态
    result = parse_proc()
    for state, count in result.items():
        print(f"{state}: {count}")
