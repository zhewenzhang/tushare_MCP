import os
from typing import Optional
import tushare as ts
from fastmcp import FastMCP
import pandas as pd

# 创建MCP服务器实例
mcp = FastMCP("Tushare Stock Info")

def get_tushare_token() -> Optional[str]:
    """获取Tushare token"""
    return os.getenv("TUSHARE_TOKEN")

def set_tushare_token(token: str):
    """设置Tushare token"""
    os.environ["TUSHARE_TOKEN"] = token
    ts.set_token(token)

@mcp.tool()
def list_tools() -> str:
    """列出所有可用的工具"""
    return """可用工具列表：
1. setup_tushare_token(token: str) - 设置Tushare API token
2. check_token_status() - 检查token状态
3. get_stock_basic_info(ts_code="", name="") - 获取股票基本信息
4. search_stocks(keyword: str) - 搜索股票
5. get_income_statement(ts_code, start_date="", end_date="", report_type="1") - 获取利润表数据"""

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

def format_income_statement_analysis(df: pd.DataFrame) -> str:
    """
    格式化利润表分析输出
    
    参数:
        df: 包含利润表数据的DataFrame
    """
    if df.empty:
        return "未找到符合条件的利润表数据"
        
    # 按照报告期末排序
    df = df.sort_values('end_date')
    
    # 提取年份和季度信息
    df['year'] = df['end_date'].str[:4]
    df['quarter'] = df['end_date'].str[4:6].map({'03': 'Q1', '06': 'Q2', '09': 'Q3', '12': 'Q4'})
    df['period'] = df['year'] + df['quarter']
    
    # 准备表头
    header = ["项目"] + df['period'].tolist()
    
    # 准备数据行
    rows = []
    metrics = {
        'total_revenue': '营业总收入',
        'revenue': '营业收入',
        'total_cogs': '营业总成本',
        'oper_cost': '营业成本',
        'sell_exp': '销售费用',
        'admin_exp': '管理费用',
        'fin_exp': '财务费用',
        'operate_profit': '营业利润',
        'total_profit': '利润总额',
        'n_income': '净利润',
        'basic_eps': '每股收益'
    }
    
    for key, name in metrics.items():
        row = [name]
        for _, period_data in df.iterrows():
            value = period_data[key]
            # 格式化数值（单位：亿元）
            if key != 'basic_eps':
                value = f"{float(value)/100000000:.2f}亿" if pd.notna(value) else '-'
            else:
                value = f"{float(value):.2f}" if pd.notna(value) else '-'
            row.append(value)
        rows.append(row)
    
    # 生成表格
    table = []
    table.append(" | ".join([f"{col:^12}" for col in header]))
    table.append("-" * (14 * len(header)))
    for row in rows:
        table.append(" | ".join([f"{col:^12}" for col in row]))
    
    # 计算同比增长率
    def calc_yoy(series):
        if len(series) >= 2:
            return (series.iloc[-1] - series.iloc[-2]) / abs(series.iloc[-2]) * 100
        return None
    
    # 计算环比增长率
    def calc_qoq(series):
        if len(series) >= 2:
            return (series.iloc[-1] - series.iloc[-2]) / abs(series.iloc[-2]) * 100
        return None
    
    # 生成分析报告
    analysis = []
    analysis.append("\n📊 财务分析报告")
    analysis.append("=" * 50)
    
    # 1. 收入分析
    analysis.append("\n一、收入分析")
    analysis.append("-" * 20)
    
    # 1.1 营收规模与增长
    revenue_yoy = calc_yoy(df['total_revenue'])
    revenue_qoq = calc_qoq(df['total_revenue'])
    latest_revenue = float(df.iloc[-1]['total_revenue'])/100000000
    
    analysis.append("1. 营收规模与增长：")
    analysis.append(f"   • 当期营收：{latest_revenue:.2f}亿元")
    if revenue_yoy is not None:
        analysis.append(f"   • 同比变动：{revenue_yoy:+.2f}%")
    if revenue_qoq is not None:
        analysis.append(f"   • 环比变动：{revenue_qoq:+.2f}%")
    
    # 2. 盈利能力分析
    analysis.append("\n二、盈利能力分析")
    analysis.append("-" * 20)
    
    # 2.1 利润规模与增长
    latest = df.iloc[-1]
    profit_yoy = calc_yoy(df['n_income'])
    profit_qoq = calc_qoq(df['n_income'])
    latest_profit = float(latest['n_income'])/100000000
    
    analysis.append("1. 利润规模与增长：")
    analysis.append(f"   • 当期净利润：{latest_profit:.2f}亿元")
    if profit_yoy is not None:
        analysis.append(f"   • 同比变动：{profit_yoy:+.2f}%")
    if profit_qoq is not None:
        analysis.append(f"   • 环比变动：{profit_qoq:+.2f}%")
    
    # 2.2 盈利能力指标
    gross_margin = ((latest['total_revenue'] - latest['oper_cost']) / latest['total_revenue']) * 100
    operating_margin = (latest['operate_profit'] / latest['total_revenue']) * 100
    net_margin = (latest['n_income'] / latest['total_revenue']) * 100
    
    analysis.append("\n2. 盈利能力指标：")
    analysis.append(f"   • 毛利率：{gross_margin:.2f}%")
    analysis.append(f"   • 营业利润率：{operating_margin:.2f}%")
    analysis.append(f"   • 净利润率：{net_margin:.2f}%")
    
    # 3. 成本费用分析
    analysis.append("\n三、成本费用分析")
    analysis.append("-" * 20)
    
    # 3.1 成本费用结构
    total_revenue = float(latest['total_revenue'])
    cost_structure = {
        '营业成本': (latest['oper_cost'] / total_revenue) * 100,
        '销售费用': (latest['sell_exp'] / total_revenue) * 100,
        '管理费用': (latest['admin_exp'] / total_revenue) * 100,
        '财务费用': (latest['fin_exp'] / total_revenue) * 100
    }
    
    analysis.append("1. 成本费用结构（占营收比）：")
    for item, ratio in cost_structure.items():
        analysis.append(f"   • {item}率：{ratio:.2f}%")
    
    # 3.2 费用变动分析
    analysis.append("\n2. 主要费用同比变动：")
    expense_items = {
        '销售费用': ('sell_exp', calc_yoy(df['sell_exp'])),
        '管理费用': ('admin_exp', calc_yoy(df['admin_exp'])),
        '财务费用': ('fin_exp', calc_yoy(df['fin_exp']))
    }
    
    for name, (_, yoy) in expense_items.items():
        if yoy is not None:
            analysis.append(f"   • {name}：{yoy:+.2f}%")
    
    # 4. 每股指标
    analysis.append("\n四、每股指标")
    analysis.append("-" * 20)
    latest_eps = float(latest['basic_eps'])
    eps_yoy = calc_yoy(df['basic_eps'])
    
    analysis.append(f"• 基本每股收益：{latest_eps:.4f}元")
    if eps_yoy is not None:
        analysis.append(f"• 同比变动：{eps_yoy:+.2f}%")
    
    # 5. 风险提示
    analysis.append("\n⚠️ 风险提示")
    analysis.append("-" * 20)
    analysis.append("以上分析基于历史财务数据，仅供参考。投资决策需考虑更多因素，包括但不限于：")
    analysis.append("• 行业周期与竞争态势")
    analysis.append("• 公司经营与治理状况")
    analysis.append("• 宏观经济环境")
    analysis.append("• 政策法规变化")
    
    return "\n".join(table) + "\n\n" + "\n".join(analysis)

@mcp.tool()
def get_income_statement(
    ts_code: str,
    start_date: str = "",
    end_date: str = "",
    report_type: str = "1"
) -> str:
    """
    获取利润表数据
    
    参数:
        ts_code: 股票代码（如：000001.SZ）
        start_date: 开始日期（YYYYMMDD格式，如：20230101）
        end_date: 结束日期（YYYYMMDD格式，如：20231231）
        report_type: 报告类型（1合并报表；2单季合并；3调整单季合并表；4调整合并报表；5调整前合并报表；6母公司报表；7母公司单季表；8母公司调整单季表；9母公司调整表；10母公司调整前报表；11母公司调整前合并报表；12母公司调整前报表）
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    try:
        pro = ts.pro_api()
        # 获取股票名称
        stock_info = pro.stock_basic(ts_code=ts_code)
        stock_name = stock_info.iloc[0]['name'] if not stock_info.empty else ts_code
        
        params = {
            'ts_code': ts_code,
            'fields': 'ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps,total_revenue,revenue,int_income,prem_earned,comm_income,n_commis_income,n_oth_income,n_oth_b_income,prem_income,out_prem,une_prem_reser,reins_income,n_sec_tb_income,n_sec_uw_income,n_asset_mg_income,oth_b_income,fv_value_chg_gain,invest_income,ass_invest_income,forex_gain,total_cogs,oper_cost,int_exp,comm_exp,biz_tax_surchg,sell_exp,admin_exp,fin_exp,assets_impair_loss,prem_refund,compens_payout,reser_insur_liab,div_payt,reins_exp,oper_exp,compens_payout_refu,insur_reser_refu,reins_cost_refund,other_bus_cost,operate_profit,non_oper_income,non_oper_exp,nca_disploss,total_profit,income_tax,n_income,n_income_attr_p,minority_gain,oth_compr_income,t_compr_income,compr_inc_attr_p,compr_inc_attr_m_s,ebit,ebitda,insurance_exp,undist_profit,distable_profit,update_flag'
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        df = pro.income(**params)
        
        if df.empty:
            return "未找到符合条件的利润表数据"
            
        # 获取报表类型描述
        report_types = {
            "1": "合并报表",
            "2": "单季合并",
            "3": "调整单季合并表",
            "4": "调整合并报表",
            "5": "调整前合并报表",
            "6": "母公司报表",
            "7": "母公司单季表",
            "8": "母公司调整单季表",
            "9": "母公司调整表",
            "10": "母公司调整前报表",
            "11": "母公司调整前合并报表",
            "12": "母公司调整前报表"
        }
        report_type_desc = report_types.get(report_type, "未知类型")
        
        # 构建输出标题
        title = f"我查询到了 {stock_name}（{ts_code}）的{report_type_desc}利润数据，如下呈现：\n\n"
        
        # 格式化数据并生成分析
        result = format_income_statement_analysis(df)
        
        return title + result
        
    except Exception as e:
        return f"查询失败：{str(e)}"

@mcp.prompt()
def income_statement_query() -> str:
    """利润表查询提示模板"""
    return """请提供以下信息来查询利润表：

1. 股票代码（必填，如：000001.SZ）

2. 时间范围（可选）：
   - 开始日期（YYYYMMDD格式，如：20230101）
   - 结束日期（YYYYMMDD格式，如：20231231）

3. 报告类型（可选，默认为合并报表）：
   1 = 合并报表（默认）
   2 = 单季合并
   3 = 调整单季合并表
   4 = 调整合并报表
   5 = 调整前合并报表
   6 = 母公司报表
   7 = 母公司单季表
   8 = 母公司调整单季表
   9 = 母公司调整表
   10 = 母公司调整前报表
   11 = 母公司调整前合并报表
   12 = 母公司调整前报表

示例查询：
1. 查询最新报表：
   "查询平安银行(000001.SZ)的最新利润表"

2. 查询指定时间范围：
   "查询平安银行2023年的利润表"
   "查询平安银行2023年第一季度的利润表"

3. 查询特定报表类型：
   "查询平安银行的母公司报表"
   "查询平安银行2023年的单季合并报表"

请告诉我您想查询的内容："""

if __name__ == "__main__":
    mcp.run() 