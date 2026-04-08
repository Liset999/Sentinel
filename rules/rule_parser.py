import os
import re
import yaml


def load_rules_with_env(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- SRE 核心逻辑：动态替换表达式中的阈值 ---
    # 如果环境变量里有 MEM_THRESHOLD，就强行把 expr 里的数字换掉
    env_vars = {
        "sentinel_memory_usage": os.environ.get("MEM_THRESHOLD", "80"),
        "sentinel_loadavg": os.environ.get("LOAD_THRESHOLD", "4.0"),
        # ... 可以继续添加其他对应关系
    }

    for metric, value in env_vars.items():
        # 正则：匹配 监控指标 > 数字，并把数字换成环境变量的值
        content = re.sub(rf"({metric}.*?>\s*)[\d\.]+", rf"\1{value}", content)

    return yaml.safe_load(content)


if __name__ == '__main__':
    rules_data = load_rules_with_env("rules/default_rules.yaml")
    print("🎯 Sentinel 动态引擎启动成功：")

    if rules_data and 'groups' in rules_data:
        for group in rules_data['groups']:
            print(f"--- 规则组: {group.get('name')} ---")
            for rule in group.get('rules', []):
                print(f"✅ 检测项: {rule.get('alert'):20} | 动态阈值: {rule.get('expr')}")