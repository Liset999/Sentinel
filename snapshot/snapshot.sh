#!/bin/bash

# ==========================================
# 脚本名称: Sentinel 快照生成工具
# 脚本功能: 一键生成故障现场快照，固定保存核心命令输出
# ==========================================


# 1. 定义变量：时间和文件路径
# 设置快照保存的目录
SNAPSHOT_DIR="artifacts/snapshots"

# 获取当前时间，格式为：年月日_时分秒
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 拼接出完整的文件路径和文件名
FILE_NAME="${SNAPSHOT_DIR}/snapshot_${TIMESTAMP}.txt"

# 测试一下，看看生成的文件名长什么样
echo "准备生成的快照文件路径是：$FILE_NAME"


# 2. 执行排查命令并保存到快照文件
# 第 1 个：记录内存使用情况
echo "========== 1. free (内存状态) ==========" >> "${FILE_NAME}"
free -h >> "${FILE_NAME}"
echo "" >> "${FILE_NAME}"

# 第 2 个：记录 CPU 和进程资源占用
echo "========== 2. top (CPU及进程概览) ==========" >> "${FILE_NAME}"
top -b -n 1 | head -n 20 >> "${FILE_NAME}"
echo "" >> "${FILE_NAME}"

# 第 3 个：记录完整的进程列表
echo "========== 3. ps (进程全景图) ==========" >> "${FILE_NAME}"
ps -ef >> "${FILE_NAME}"
echo "" >> "${FILE_NAME}"

# 第 4 个：记录网络连接和端口状态
echo "========== 4. ss (网络与端口) ==========" >> "${FILE_NAME}"
ss -ntlp >> "${FILE_NAME}"
echo "" >> "${FILE_NAME}"

# 第 5 个：记录内核和系统底层日志
echo "========== 5. dmesg (内核与系统日志) ==========" >> "${FILE_NAME}"
dmesg -T | tail -n 50 >> "${FILE_NAME}"
echo "" >> "${FILE_NAME}"

# ==========================================
# 3. 脚本执行完毕，打印成功提示
# ==========================================
echo "✅ 快照已保存：${FILE_NAME}"
