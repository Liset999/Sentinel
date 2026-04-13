import asyncio
import aiohttp
from aiohttp import ClientTimeout
import collections

# ===================== 压测配置 =====================
TARGET_URL = "http://127.0.0.1:8080/"
CONCURRENCY = 50  # 固定50个并发协程
REQUEST_TIMEOUT = 2 # 2秒没回应，算失败
REPORT_INTERVAL = 1 # 每秒报一次成绩

# 强制服务端断开连接，规避客户端 TIME_WAIT
HEADERS = {"Connection": "close"}

# ===================== 全局指标计数器 =====================
success_count = 0
fail_count = 0
error_stats = collections.Counter()


# ===================== 异步请求函数（已删除 semaphore） =====================
async def fetch(session: aiohttp.ClientSession):
    """单次异步短连接请求（无冗余锁，极致性能）"""
    global success_count, fail_count
    try:
        async with session.get(
                TARGET_URL,
                headers=HEADERS,
                timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as resp:
            # 仅读取状态码，轻量化压测
            _ = resp.status
            success_count += 1

    # 全量异常捕获，保证压测不崩溃
    except Exception as e:  # 既然捕获所有异常，直接写 Exception 即可涵盖前面两个
        fail_count += 1
        err_type = type(e).__name__
        error_stats[err_type] += 1


# ===================== 压测工作协程（已删除 semaphore） =====================
async def worker(session: aiohttp.ClientSession):
    """无限循环压测，请求完成立刻发起下一个"""
    while True:
        await fetch(session)


# ===================== 旁路指标统计协程 =====================
async def metrics_reporter():
    global success_count, fail_count
    while True:
        await asyncio.sleep(REPORT_INTERVAL)
        total = success_count + fail_count
        qps = total
        success_rate = (success_count / total * 100) if total > 0 else 0.0
        print(
            f"[指标统计] QPS: {qps:>4} | 成功: {success_count:>4} | 失败: {fail_count:>4} | 成功率: {success_rate:.1f}%")
        if error_stats:
            # 打印当前秒的错误类型分布
            print(f"    [错误分布] {dict(error_stats)}")
            error_stats.clear()
        success_count = 0
        fail_count = 0


# ===================== 主函数（已删除 semaphore） =====================
async def short_conn_client():
    # 强制短连接，杜绝长连接复用
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        # 核心：直接创建50个无限循环的worker = 固定50并发（无任何冗余）
        workers = [worker(session) for _ in range(CONCURRENCY)]
        # 启动指标统计
        reporter = metrics_reporter()

        # 并发运行所有任务
        await asyncio.gather(*workers, reporter)


if __name__ == "__main__":
    print("=== 工业级异步短连接压测客户端已启动 ===")
    print(f"目标: {TARGET_URL} | 并发: {CONCURRENCY} | 超时: {REQUEST_TIMEOUT}s\n")
    try:
        asyncio.run(short_conn_client())
    except KeyboardInterrupt:
        print("\n[!] 接收到退出信号 (Ctrl+C)，压测已停止。")