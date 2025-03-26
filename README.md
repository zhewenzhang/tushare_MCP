# Tushare MCP Server

<div align="center">

基于 Model Context Protocol (MCP) 的智能股票数据助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

</div>

## 🚀 核心功能

### 1. 股票基础信息查询
- 支持通过股票代码（如：000001.SZ）精确查询
- 支持通过股票名称（如：平安银行）模糊查询
- 返回信息包含：
  - 股票代码和名称
  - 所属行业和地区
  - 上市日期
  - 市场类型
  - 交易状态

### 2. 智能股票搜索
- 支持模糊关键词搜索
- 同时匹配股票代码和名称
- 支持行业关键词搜索（如："新能源"、"科技"）
- 返回匹配度最高的股票列表

### 3. 财务报表分析
- 支持查询上市公司利润表数据
- 灵活的时间范围查询（年报、季报、半年报）
- 多种报表类型支持（合并报表、母公司报表等）
- 主要指标一目了然：
  - 每股收益
  - 营业收入和成本
  - 期间费用
  - 利润指标
- 支持历史数据对比分析

### 4. 安全的Token管理
- 交互式Token配置流程
- 本地安全存储（加密保存）
- Token有效性自动验证
- 定期Token状态检查

## 🎯 使用场景

1. **投资研究**
   ```
   "帮我查找所有新能源相关的股票"
   "查询比亚迪的基本信息"
   "获取平安银行2023年的利润表"
   ```

2. **财务分析**
   ```
   "查看腾讯控股最新一期合并报表"
   "对比阿里巴巴近三年的利润变化"
   "分析小米集团的季度利润趋势"
   ```

3. **行业分析**
   ```
   "列出所有医药行业的股票"
   "查找深圳地区的科技公司"
   ```

4. **报表查询**
   ```
   "查询平安银行2023年第一季度的利润表"
   "获取比亚迪的母公司报表"
   "查看茅台近5年的年度利润表"
   ```

## 🛠️ 技术特点

- 基于MCP协议，支持与Claude等AI助手自然对话
- 实时连接Tushare Pro数据源
- 智能错误处理和提示
- 支持并发请求处理
- 数据缓存优化

## 📦 安装说明

### 环境要求
- Python 3.8+
- Tushare Pro账号和API Token

### 快速开始

1. 安装包
```bash
git clone https://github.com/zhewenzhang/tushare_MCP.git
cd tushare_MCP
pip install -r requirements.txt
```

2. 启动服务
```bash
python server.py
```

3. 在Claude中安装
```bash
mcp install server.py
```

## 🔑 首次配置

1. **获取Token**
   - 访问 [Tushare Token页面](https://tushare.pro/user/token)
   - 登录获取API Token

2. **配置Token**
   ```
   对Claude说：请帮我配置Tushare token
   ```

3. **验证配置**
   ```
   对Claude说：请检查token状态
   ```

## 📚 API参考

### 工具函数

1. **股票查询**
```python
get_stock_basic_info(ts_code="", name="")
# 示例：get_stock_basic_info(ts_code="000001.SZ")
```

2. **股票搜索**
```python
search_stocks(keyword="")
# 示例：search_stocks(keyword="新能源")
```

3. **利润表查询**
```python
get_income_statement(ts_code="", start_date="", end_date="", report_type="1")
# 示例：get_income_statement(ts_code="000001.SZ", start_date="20230101", end_date="20231231")
```

4. **Token管理**
```python
setup_tushare_token(token="")
check_token_status()
```

## 🔒 数据安全

- Token存储：用户主目录下的`.tushare_mcp/.env`
- 环境变量：使用python-dotenv安全管理
- 数据传输：HTTPS加密

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件 