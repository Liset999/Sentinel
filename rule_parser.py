import os
import yaml
from dotenv import load_dotenv

# 显式加载 .env 文件
load_dotenv()


def load_rules_with_env(filepath: str = "rules/default_rules.yaml"):
    """读取规则文件，用 .env 里的阈值动态替换"""
    with open(filepath, 'r', encoding='utf-8') as f:
        rules_data = yaml.safe_load(f)

    # 从 .env 读取阈值
    env_vars = {
        "sentinel_memory_usage": os.environ.get("MEM_THRESHOLD", "80"),
        "sentinel_loadavg": os.environ.get("LOAD_THRESHOLD", "4.0"),
        "sentinel_tcp_connections": os.environ.get("TIME_WAIT_THRESHOLD", "50"),
        "sentinel_process_count": os.environ.get("ZOMBIE_THRESHOLD", "0"),
    }

    print("📌 当前读取到的 .env 阈值：")
    for metric, value in env_vars.items():
        print(f"   {metric:25} = {value}")

    # 简单字符串替换（避免复杂正则冲突）
    for group in rules_data.get("groups", []):
        for rule in group.get("rules", []):
            expr = str(rule.get("expr", ""))
            if not expr:
                continue

            for metric, value in env_vars.items():
                if metric in expr and ">" in expr:
                    # 把 > 后面的数字全部替换
                    left = expr.split(">", 1)[0].strip()
                    rule["expr"] = f"{left} > {value}"

    return rules_data


def save_processed_rules(rules_data, output_path: str = "rules/processed_rules.yaml"):
    """保存处理后的规则"""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(rules_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\n✅ 动态规则生成成功！已写入 → {output_path}")


if __name__ == '__main__':
    print("🎯 Sentinel 动态规则引擎启动...")

    rules_data = load_rules_with_env()

    if rules_data and 'groups' in rules_data:
        save_processed_rules(rules_data)

        print("\n当前生效的动态规则：")
        for group in rules_data.get('groups', []):
            for rule in group.get('rules', []):
                print(f"   • {rule.get('alert'):20} → {rule.get('expr')}")
    else:
        print("❌ 规则解析失败")