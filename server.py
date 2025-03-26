import os
from pathlib import Path
from typing import Optional
import tushare as ts
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv, set_key
import pandas as pd

# 创建MCP服务器实例
mcp = FastMCP("Tushare Stock Info")

# 环境变量文件路径
ENV_FILE = Path.home() / ".tushare_mcp" / ".env"

def init_env_file():
    """初始化环境变量文件"""
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not ENV_FILE.exists():
        ENV_FILE.touch()
    load_dotenv(ENV_FILE)

def get_tushare_token() -> Optional[str]:
    """获取Tushare token"""
    init_env_file()
    return os.getenv("TUSHARE_TOKEN")

def set_tushare_token(token: str):
    """设置Tushare token"""
    init_env_file()
    set_key(ENV_FILE, "TUSHARE_TOKEN", token)
    # 初始化tushare
    ts.set_token(token)

@mcp.prompt()
def configure_token() -> str:
    """配置Tushare token的提示模板"""
    return """请提供您的Tushare API token。
您可以在 https://tushare.pro/user/token 获取您的token。
如果您还没有Tushare账号，请先在 https://tushare.pro/register 注册。

请输入您的token:"""

@mcp.tool()
def setup_tushare_token(token: str) -> str:
    """设置Tushare API token"""
    try:
        set_tushare_token(token)
        # 测试token是否有效
        ts.pro_api()
        return "Token配置成功！您现在可以使用Tushare的API功能了。"
    except Exception as e:
        return f"Token配置失败：{str(e)}"

@mcp.tool()
def check_token_status() -> str:
    """检查Tushare token状态"""
    token = get_tushare_token()
    if not token:
        return "未配置Tushare token。请使用configure_token提示来设置您的token。"
    try:
        ts.pro_api()
        return "Token配置正常，可以使用Tushare API。"
    except Exception as e:
        return f"Token无效或已过期：{str(e)}"

@mcp.tool()
def get_stock_basic_info(ts_code: str = "", name: str = "") -> str:
    """
    获取股票基本信息
    
    参数:
        ts_code: 股票代码（如：000001.SZ）
        name: 股票名称（如：平安银行）
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    try:
        pro = ts.pro_api()
        filters = {}
        if ts_code:
            filters['ts_code'] = ts_code
        if name:
            filters['name'] = name
            
        df = pro.stock_basic(**filters)
        if df.empty:
            return "未找到符合条件的股票"
            
        # 格式化输出
        result = []
        for _, row in df.iterrows():
            # 获取所有可用的列
            available_fields = row.index.tolist()
            
            # 构建基本信息
            info_parts = []
            
            # 必要字段
            if 'ts_code' in available_fields:
                info_parts.append(f"股票代码: {row['ts_code']}")
            if 'name' in available_fields:
                info_parts.append(f"股票名称: {row['name']}")
                
            # 可选字段
            optional_fields = {
                'area': '所属地区',
                'industry': '所属行业',
                'list_date': '上市日期',
                'market': '市场类型',
                'exchange': '交易所',
                'curr_type': '币种',
                'list_status': '上市状态',
                'delist_date': '退市日期'
            }
            
            for field, label in optional_fields.items():
                if field in available_fields and not pd.isna(row[field]):
                    info_parts.append(f"{label}: {row[field]}")
            
            info = "\n".join(info_parts)
            info += "\n------------------------"
            result.append(info)
            
        return "\n".join(result)
        
    except Exception as e:
        return f"查询失败：{str(e)}"

@mcp.tool()
def search_stocks(keyword: str) -> str:
    """
    搜索股票
    
    参数:
        keyword: 关键词（可以是股票代码的一部分或股票名称的一部分）
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    try:
        pro = ts.pro_api()
        df = pro.stock_basic()
        
        # 在代码和名称中搜索关键词
        mask = (df['ts_code'].str.contains(keyword, case=False)) | \
               (df['name'].str.contains(keyword, case=False))
        results = df[mask]
        
        if results.empty:
            return "未找到符合条件的股票"
            
        # 格式化输出
        output = []
        for _, row in results.iterrows():
            output.append(f"{row['ts_code']} - {row['name']}")
            
        return "\n".join(output)
        
    except Exception as e:
        return f"搜索失败：{str(e)}"

if __name__ == "__main__":
    mcp.run() 