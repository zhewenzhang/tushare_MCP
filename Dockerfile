FROM python:3.10-slim as builder

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /build

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY server.py .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 启动MCP服务器
CMD ["python", "server.py"] 