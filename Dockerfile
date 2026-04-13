# 1. 使用官方轻量级 Python 运行环境作为基础镜像
FROM python:3.9-slim

# 2. 设置容器内部的工作目录
WORKDIR /app

# 3. 设置环境变量，确保 Python 输出直接打印到控制台，不留缓存
ENV PYTHONUNBUFFERED=1

# ==========================================
# 👇 新增：安装系统运维工具 (procps, iproute2, kmod)
# ==========================================
RUN apt-get update && apt-get install -y \
    procps \
    iproute2 \
    kmod \
    && rm -rf /var/lib/apt/lists/*

# 4. 先复制依赖文件（利用 Docker 缓存机制，若依赖未变则跳过安装阶段）
COPY requirements.txt .

# 5. 安装依赖
# 使用 --no-cache-dir 减少镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制项目所有代码到容器中
COPY . .

# 7. 声明容器监听的端口（对应你 app.py 中的 start_http_server）
EXPOSE 8000

# 8. 启动程序
CMD ["python", "-m", "exporter.app"]