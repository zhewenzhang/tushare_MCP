# Tushare MCP Server

这是一个基于MCP (Model Context Protocol)的Tushare数据查询服务器，可以让您方便地通过AI助手查询股票基本信息。

## 功能特点

- Token配置和验证
- 股票基本信息查询
- 股票搜索功能
- 安全的token存储

## 安装

1. 确保您已安装Python 3.8或更高版本
2. 克隆此仓库
3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行服务器：
```bash
python server.py
```

2. 在Claude Desktop中安装此服务器：
```bash
mcp install server.py
```

3. 首次使用时，您需要配置Tushare token：
   - 访问 https://tushare.pro/user/token 获取您的token
   - 使用configure_token提示来设置token
   - 使用check_token_status工具验证token是否配置成功

## 可用工具

1. `setup_tushare_token(token: str)`
   - 设置Tushare API token
   - 参数：token - Tushare API token字符串

2. `check_token_status()`
   - 检查当前token的配置状态

3. `get_stock_basic_info(ts_code: str = "", name: str = "")`
   - 获取股票的基本信息
   - 参数：
     - ts_code: 股票代码（如：000001.SZ）
     - name: 股票名称（如：平安银行）

4. `search_stocks(keyword: str)`
   - 搜索股票
   - 参数：
     - keyword: 搜索关键词（可以是股票代码或名称的一部分）

## 提示模板

1. `configure_token`
   - 引导用户配置Tushare token的交互式提示

## 安全说明

- token存储在用户主目录下的.tushare_mcp/.env文件中
- 使用python-dotenv进行安全的环境变量管理
- token不会被暴露在代码或日志中

## 示例用法

1. 配置token：
```
请使用configure_token提示来设置您的token
```

2. 查询股票信息：
```
请帮我查询平安银行的基本信息
```

3. 搜索股票：
```
请帮我搜索包含"科技"的股票
``` 