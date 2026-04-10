# rules/watcher.py
import os
import time
import requests
import subprocess

# 我们要重点盯防的文件
WATCH_FILES = [".env", "rules/default_rules.yaml"]
# Prometheus 的热重载接口
PROMETHEUS_RELOAD_URL = "http://prometheus:9090/-/reload"


def get_latest_mtime():
    """获取文件最新的修改时间戳"""
    latest_time = 0
    for f in WATCH_FILES:
        if os.path.exists(f):
            latest_time = max(latest_time, os.path.getmtime(f))
    return latest_time


def main():
    print("👀 Watcher Sidecar 监听服务已启动，正在实时监控 .env 和规则模板...")
    last_mtime = get_latest_mtime()

    # 启动时先强制生成一次，确保 Prometheus 启动时有规则可用
    subprocess.run(["python", "rules/rule_parser.py"])

    while True:
        time.sleep(5)  # 每 5 秒轮询一次
        current_mtime = get_latest_mtime()

        # 如果当前时间戳大于上一次的时间戳，说明文件被改了！
        if current_mtime > last_mtime:
            print(f"\n🔄 [{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到配置文件发生变化，开始热更新...")

            # 1. 重新执行你的解析脚本，生成新的 processed_rules.yaml
            subprocess.run(["python", "rules/rule_parser.py"])

            # 2. 通知 Prometheus 重载配置
            try:
                response = requests.post(PROMETHEUS_RELOAD_URL)
                if response.status_code == 200:
                    print("✅ Prometheus 配置热重载成功！新阈值已生效。")
                else:
                    print(f"⚠️ Prometheus 返回异常状态码: {response.status_code}")
            except Exception as e:
                print(f"❌ 无法连接到 Prometheus: {e}")

            last_mtime = current_mtime


if __name__ == "__main__":
    main()