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
def get_daily_basic_indicators(
    ts_code: str = "",
    trade_date: str = "",
    start_date: str = "",
    end_date: str = ""
) -> str:
    """
    获取股票每日重要的基本面指标
    
    参数:
        ts_code: 股票代码（与ts_code和trade_date二选一）
        trade_date: 交易日期（YYYYMMDD格式，如：20240801）
        start_date: 开始日期（YYYYMMDD格式，如：20240701）
        end_date: 结束日期（YYYYMMDD格式，如：20240731）
    
    返回指标:
        - 价格数据：收盘价
        - 交易数据：换手率、量比
        - 估值指标：市盈率(PE)、市净率(PB)、市销率(PS)
        - 股本数据：总股本、流通股本、自由流通股本
        - 市值数据：总市值、流通市值
        - 分红数据：股息率
    
    示例:
        - 查询单股指标：ts_code="000001.SZ", trade_date="20240801"
        - 查询全市场：trade_date="20240801"
        - 查询历史数据：ts_code="000001.SZ", start_date="20240701", end_date="20240731"
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    # 参数验证
    if not ts_code and not trade_date:
        return "请至少提供股票代码(ts_code)或交易日期(trade_date)中的一个参数"
        
    try:
        pro = ts.pro_api()
        
        # 构建查询参数
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        # 调用每日指标接口
        df = pro.daily_basic(**params)
        
        if df.empty:
            return "未找到符合条件的基本面指标数据\n\n请检查：\n1. 股票代码是否正确\n2. 交易日期是否为交易日\n3. 是否有足够的积分权限（需至少2000积分）"
            
        # 按股票代码和交易日期排序
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 格式化输出
        result = []
        result.append("📈 股票每日基本面指标")
        result.append("=" * 60)
        
        # 判断显示模式
        is_single_stock = ts_code and len(df) <= 10
        is_single_date = trade_date and not ts_code
        
        if is_single_stock:
            # 单股详细模式
            stock_code = df.iloc[0]['ts_code']
            
            # 获取股票名称
            try:
                stock_info = pro.stock_basic(ts_code=stock_code)
                stock_name = stock_info.iloc[0]['name'] if not stock_info.empty else stock_code
            except:
                stock_name = stock_code
                
            result.append(f"🏢 {stock_name}（{stock_code}）")
            result.append(f"数据条数: {len(df)}条")
            result.append("")
            
            # 详细数据展示
            for _, row in df.iterrows():
                trade_date_display = str(row['trade_date'])
                result.append(f"📅 交易日期: {trade_date_display}")
                result.append("-" * 50)
                
                # 价格信息
                close_price = f"{row['close']:.2f}元" if pd.notna(row['close']) else '-'
                result.append(f"💰 收盘价: {close_price}")
                
                # 交易指标
                turnover_rate = f"{row['turnover_rate']:.2f}%" if pd.notna(row['turnover_rate']) else '-'
                turnover_rate_f = f"{row['turnover_rate_f']:.2f}%" if pd.notna(row['turnover_rate_f']) else '-'
                volume_ratio = f"{row['volume_ratio']:.2f}" if pd.notna(row['volume_ratio']) else '-'
                
                result.append(f"🔄 换手率: {turnover_rate}")
                result.append(f"🔄 换手率(自由流通): {turnover_rate_f}")
                result.append(f"📈 量比: {volume_ratio}")
                
                # 估值指标
                pe = f"{row['pe']:.2f}" if pd.notna(row['pe']) else '-'
                pe_ttm = f"{row['pe_ttm']:.2f}" if pd.notna(row['pe_ttm']) else '-'
                pb = f"{row['pb']:.2f}" if pd.notna(row['pb']) else '-'
                ps = f"{row['ps']:.2f}" if pd.notna(row['ps']) else '-'
                ps_ttm = f"{row['ps_ttm']:.2f}" if pd.notna(row['ps_ttm']) else '-'
                
                result.append(f"📊 市盈率(PE): {pe}")
                result.append(f"📊 市盈率(PE TTM): {pe_ttm}")
                result.append(f"📊 市净率(PB): {pb}")
                result.append(f"📊 市销率(PS): {ps}")
                result.append(f"📊 市销率(PS TTM): {ps_ttm}")
                
                # 股息率
                dv_ratio = f"{row['dv_ratio']:.2f}%" if pd.notna(row['dv_ratio']) else '-'
                dv_ttm = f"{row['dv_ttm']:.2f}%" if pd.notna(row['dv_ttm']) else '-'
                
                result.append(f"💵 股息率: {dv_ratio}")
                result.append(f"💵 股息率(TTM): {dv_ttm}")
                
                # 股本和市值
                total_share = f"{row['total_share']:.0f}万股" if pd.notna(row['total_share']) else '-'
                float_share = f"{row['float_share']:.0f}万股" if pd.notna(row['float_share']) else '-'
                free_share = f"{row['free_share']:.0f}万股" if pd.notna(row['free_share']) else '-'
                
                result.append(f"📈 总股本: {total_share}")
                result.append(f"📈 流通股本: {float_share}")
                result.append(f"📈 自由流通股本: {free_share}")
                
                # 市值信息（转换为亿元）
                total_mv = f"{row['total_mv']/10000:.2f}亿元" if pd.notna(row['total_mv']) else '-'
                circ_mv = f"{row['circ_mv']/10000:.2f}亿元" if pd.notna(row['circ_mv']) else '-'
                
                result.append(f"💰 总市值: {total_mv}")
                result.append(f"💰 流通市值: {circ_mv}")
                result.append("")
                
        else:
            # 表格模式
            result.append(f"数据条数: {len(df)}条")
            result.append("")
            
            if is_single_date:
                # 单日全市场模式
                headers = ["股票代码", "收盘价", "换手率%", "量比", "PE", "PB", "总市值(亿)"]
            else:
                # 历史数据模式
                headers = ["股票代码", "交易日期", "收盘价", "换手率%", "PE", "PB"]
            
            result.append(" | ".join([f"{h:^12}" for h in headers]))
            result.append("-" * (14 * len(headers)))
            
            for _, row in df.head(50).iterrows():  # 限制显示前50条
                ts_code_display = row['ts_code']
                
                close_price = f"{row['close']:.2f}" if pd.notna(row['close']) else '-'
                turnover_rate = f"{row['turnover_rate']:.2f}" if pd.notna(row['turnover_rate']) else '-'
                volume_ratio = f"{row['volume_ratio']:.2f}" if pd.notna(row['volume_ratio']) else '-'
                pe = f"{row['pe']:.2f}" if pd.notna(row['pe']) else '-'
                pb = f"{row['pb']:.2f}" if pd.notna(row['pb']) else '-'
                
                if is_single_date:
                    # 单日数据显示
                    total_mv = f"{row['total_mv']/10000:.1f}" if pd.notna(row['total_mv']) else '-'
                    data_row = [ts_code_display, close_price, turnover_rate, volume_ratio, pe, pb, total_mv]
                else:
                    # 历史数据显示
                    trade_date_display = str(row['trade_date'])
                    data_row = [ts_code_display, trade_date_display, close_price, turnover_rate, pe, pb]
                
                result.append(" | ".join([f"{d:^12}" for d in data_row]))
            
            if len(df) > 50:
                result.append(f"\n... 还有{len(df)-50}条数据未显示 ...")
        
        # 市场统计分析
        if len(df) > 1 and not is_single_stock:
            result.append("\n📊 市场指标统计")
            result.append("-" * 30)
            
            # PE分布统计
            pe_data = df['pe'].dropna()
            if len(pe_data) > 0:
                pe_mean = pe_data.mean()
                pe_median = pe_data.median()
                pe_min = pe_data.min()
                pe_max = pe_data.max()
                
                result.append(f"📊 PE指标统计：")
                result.append(f"  • 平均PE: {pe_mean:.2f}")
                result.append(f"  • 中位PE: {pe_median:.2f}")
                result.append(f"  • 最低PE: {pe_min:.2f}")
                result.append(f"  • 最高PE: {pe_max:.2f}")
            
            # PB分布统计
            pb_data = df['pb'].dropna()
            if len(pb_data) > 0:
                pb_mean = pb_data.mean()
                pb_median = pb_data.median()
                pb_min = pb_data.min()
                pb_max = pb_data.max()
                
                result.append(f"\n📊 PB指标统计：")
                result.append(f"  • 平均PB: {pb_mean:.2f}")
                result.append(f"  • 中位PB: {pb_median:.2f}")
                result.append(f"  • 最低PB: {pb_min:.2f}")
                result.append(f"  • 最高PB: {pb_max:.2f}")
            
            # 换手率统计
            turnover_data = df['turnover_rate'].dropna()
            if len(turnover_data) > 0:
                turnover_mean = turnover_data.mean()
                turnover_median = turnover_data.median()
                
                result.append(f"\n🔄 换手率统计：")
                result.append(f"  • 平均换手率: {turnover_mean:.2f}%")
                result.append(f"  • 中位换手率: {turnover_median:.2f}%")
            
            # 市值统计（单日数据时）
            if is_single_date:
                total_mv_data = df['total_mv'].dropna() / 10000  # 转换为亿元
                if len(total_mv_data) > 0:
                    mv_sum = total_mv_data.sum()
                    mv_mean = total_mv_data.mean()
                    
                    result.append(f"\n💰 市值统计：")
                    result.append(f"  • 市场总市值: {mv_sum:.0f}亿元")
                    result.append(f"  • 平均市值: {mv_mean:.2f}亿元")
        
        result.append("\n⚠️ 数据说明")
        result.append("-" * 20)
        result.append("• 数据更新时间：交易日15点~17点")
        result.append("• 可用于选股分析、报表展示")
        result.append("• 产损股票的PE值为空")
        result.append("• TTM：过去12个月的数据")
        result.append("• 需至少2000积分才可调取")
        result.append("• 5000积分无总量限制")
        result.append("• 股本单位：万股；市值单位：万元")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"查询失败：{str(e)}\n\n请检查：\n1. 参数格式是否正确\n2. 是否有足够的积分权限（至少2000积分）\n3. 股票代码是否存在\n4. 交易日期是否为交易日\n5. 网络连接是否正常"

@mcp.tool()
def get_financial_news(
    src: str,
    start_date: str,
    end_date: str
) -> str:
    """
    获取主流新闻网站的快讯新闻数据
    
    参数:
        src: 新闻来源（支持的来源见下方说明）
        start_date: 开始日期（格式：2018-11-20 09:00:00）
        end_date: 结束日期（格式：2018-11-20 22:05:03）
    
    支持的新闻来源:
        - sina: 新浪财经
        - wallstreetcn: 华尔街见闻
        - 10jqka: 同花顺
        - eastmoney: 东方财富
        - yuncaijing: 云财经
        - fenghuang: 凤凰新闻
        - jinrongjie: 金融界
        - cls: 财联社
        - yicai: 第一财经
    
    示例:
        - 获取今日新浪财经快讯：src="sina", start_date="2024-08-01 09:00:00", end_date="2024-08-01 18:00:00"
        - 获取华尔街见闻快讯：src="wallstreetcn", start_date="2024-08-01 09:00:00", end_date="2024-08-01 18:00:00"
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    if not src:
        return "请提供新闻来源参数（src）"
        
    if not start_date or not end_date:
        return "请提供开始和结束日期参数"
    
    # 验证新闻来源
    valid_sources = {
        'sina': '新浪财经',
        'wallstreetcn': '华尔街见闻',
        '10jqka': '同花顺',
        'eastmoney': '东方财富',
        'yuncaijing': '云财经',
        'fenghuang': '凤凰新闻',
        'jinrongjie': '金融界',
        'cls': '财联社',
        'yicai': '第一财经'
    }
    
    if src not in valid_sources:
        valid_list = "\n".join([f"  - {k}: {v}" for k, v in valid_sources.items()])
        return f"不支持的新闻来源: {src}\n\n支持的来源有：\n{valid_list}"
        
    try:
        pro = ts.pro_api()
        
        # 调用新闻接口
        df = pro.news(src=src, start_date=start_date, end_date=end_date)
        
        if df.empty:
            return f"未找到符合条件的新闻数据\n\n请检查：\n1. 日期范围是否合理\n2. 该时间段是否有新闻发布"
            
        # 按时间排序（最新的在前）
        df = df.sort_values('datetime', ascending=False)
        
        # 格式化输出
        result = []
        result.append(f"📰 {valid_sources[src]}财经快讯")
        result.append("=" * 60)
        result.append(f"查询时间: {start_date} 至 {end_date}")
        result.append(f"新闻数量: {len(df)}条")
        result.append("")
        
        # 显示新闻列表
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            # 时间格式化
            news_time = str(row['datetime'])
            
            # 标题和内容
            title = str(row['title']) if pd.notna(row['title']) else '无标题'
            content = str(row['content']) if pd.notna(row['content']) else '无内容'
            
            # 分类信息（如果有）
            channels = ""
            if 'channels' in df.columns and pd.notna(row['channels']):
                channels = f" | 🏷️ {row['channels']}"
                
            result.append(f"🔴 第{idx}条新闻")
            result.append(f"🕰️ 时间: {news_time}{channels}")
            result.append(f"📝 标题: {title}")
            result.append(f"📄 内容: {content[:200]}{'...' if len(content) > 200 else ''}")
            result.append("-" * 50)
            
            # 限制显示数量避免输出过长
            if idx >= 20:
                result.append(f"\n... 还有{len(df)-20}条新闻未显示 ...")
                break
        
        # 新闻统计
        result.append("\n📊 新闻统计")
        result.append("-" * 20)
        
        # 按小时统计新闻数量
        if 'datetime' in df.columns:
            df['hour'] = pd.to_datetime(df['datetime']).dt.hour
            hourly_stats = df['hour'].value_counts().sort_index()
            
            result.append("• 新闻时间分布：")
            for hour in sorted(hourly_stats.index):
                count = hourly_stats[hour]
                bar = "█" * min(count // 2, 20)  # 简单的柱状图
                result.append(f"  {hour:02d}时: {count}条 {bar}")
        
        # 关键词统计（简单版）
        if len(df) > 0:
            result.append("\n• 热门关键词：")
            all_content = ' '.join(df['content'].fillna('').astype(str))
            
            # 简单的关键词提取（财经相关）
            finance_keywords = [
                '股票', '上涨', '下跌', '涨停', '跌停', '交易', '投资',
                '银行', '基金', '债券', '期货', '同比', '环比', '增长',
                '亚太', '美股', 'A股', '港股', '科创板', '创业板',
                '央行', '政策', '通胀', '经济', 'GDP', 'CPI', 'PMI'
            ]
            
            keyword_counts = {}
            for keyword in finance_keywords:
                count = all_content.count(keyword)
                if count > 0:
                    keyword_counts[keyword] = count
            
            # 按频次排序
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if sorted_keywords:
                for keyword, count in sorted_keywords:
                    result.append(f"  - {keyword}: {count}次")
            else:
                result.append("  未找到常见财经关键词")
        
        result.append("\n⚠️ 数据说明")
        result.append("-" * 20)
        result.append("• 提供超过6年以上历史新闻")
        result.append("• 单次最大获取1500条新闻")
        result.append("• 可根据时间参数循环提取历史数据")
        result.append(f"• 数据来源：{valid_sources[src]}")
        result.append("• 本接口需单独开权限")
        result.append("• 新闻内容仅供参考，不作为投资建议")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"查询失败：{str(e)}\n\n请检查：\n1. 日期格式是否正确（如：2024-08-01 09:00:00）\n2. 是否有访问新闻数据的权限\n3. 新闻来源是否支持\n4. 网络连接是否正常"

@mcp.tool()
def get_realtime_stock_price(ts_code: str) -> str:
    """
    获取沪深京实时日线行情数据
    
    参数:
        ts_code: 股票代码，支持通配符方式（如：6*.SH、301*.SZ、600000.SH）
                必须带.SH/.SZ/.BJ后缀
    
    示例:
        - 获取单个股票：600000.SH
        - 获取多个股票：600000.SH,000001.SZ
        - 获取沪市所有600开头：6*.SH
        - 获取深市所有300开头：301*.SZ
        - 获取创业板所有：3*.SZ
        - 获取全市场：3*.SZ,6*.SH,0*.SZ,9*.BJ
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    if not ts_code:
        return "请提供股票代码参数（必须带.SH/.SZ/.BJ后缀）"
        
    try:
        pro = ts.pro_api()
        
        # 调用实时日线接口
        df = pro.rt_k(ts_code=ts_code)
        
        if df.empty:
            return "未找到符合条件的实时行情数据，请检查股票代码格式是否正确"
            
        # 按涨跌幅排序
        if 'pre_close' in df.columns and 'close' in df.columns:
            df['pct_chg'] = ((df['close'] - df['pre_close']) / df['pre_close'] * 100).round(2)
            df = df.sort_values('pct_chg', ascending=False)
        
        # 格式化输出
        result = []
        result.append("📈 沪深京实时日线行情")
        result.append("=" * 60)
        result.append(f"查询代码: {ts_code}")
        result.append(f"数据条数: {len(df)}条")
        result.append("")
        
        # 判断是否为单个股票查询
        is_single_stock = len(df) == 1 or ('*' not in ts_code and ',' not in ts_code)
        
        if is_single_stock and len(df) <= 5:
            # 详细模式：显示完整信息
            for _, row in df.iterrows():
                result.append(f"🏢 {row['name']}（{row['ts_code']}）")
                result.append("-" * 40)
                
                # 价格信息
                open_price = f"{row['open']:.2f}" if pd.notna(row['open']) else '-'
                high_price = f"{row['high']:.2f}" if pd.notna(row['high']) else '-'
                low_price = f"{row['low']:.2f}" if pd.notna(row['low']) else '-'
                close_price = f"{row['close']:.2f}" if pd.notna(row['close']) else '-'
                pre_close = f"{row['pre_close']:.2f}" if pd.notna(row['pre_close']) else '-'
                
                # 计算涨跌
                if pd.notna(row['close']) and pd.notna(row['pre_close']):
                    change = row['close'] - row['pre_close']
                    pct_chg = (change / row['pre_close']) * 100
                    change_str = f"{change:+.2f}"
                    pct_chg_str = f"{pct_chg:+.2f}%"
                    
                    # 添加涨跌指示符
                    if change > 0:
                        trend = "📈"
                        change_str = f"🔴+{change:.2f}"
                        pct_chg_str = f"🔴+{pct_chg:.2f}%"
                    elif change < 0:
                        trend = "📉"
                        change_str = f"🟢{change:.2f}"
                        pct_chg_str = f"🟢{pct_chg:.2f}%"
                    else:
                        trend = "➡️"
                        change_str = "0.00"
                        pct_chg_str = "0.00%"
                else:
                    trend = "❓"
                    change_str = "-"
                    pct_chg_str = "-"
                
                result.append(f"💰 最新价格: {close_price}元 {trend}")
                result.append(f"📊 昨日收盘: {pre_close}元")
                result.append(f"📈 涨跌金额: {change_str}元")
                result.append(f"📊 涨跌幅度: {pct_chg_str}")
                result.append(f"🔼 今日最高: {high_price}元")
                result.append(f"🔽 今日最低: {low_price}元")
                result.append(f"🔓 开盘价格: {open_price}元")
                
                # 成交信息
                vol = f"{row['vol']:,}股" if pd.notna(row['vol']) else '-'
                amount = f"{row['amount']:,}元" if pd.notna(row['amount']) else '-'
                num = f"{row['num']:,}笔" if pd.notna(row['num']) else '-'
                
                result.append(f"💹 成交量: {vol}")
                result.append(f"💰 成交额: {amount}")
                result.append(f"🔢 成交笔数: {num}")
                
                # 委托信息（如果有）
                if 'ask_volume1' in df.columns and pd.notna(row['ask_volume1']):
                    ask_vol = f"{row['ask_volume1']:,}股"
                    result.append(f"📤 委托卖盘: {ask_vol}")
                    
                if 'bid_volume1' in df.columns and pd.notna(row['bid_volume1']):
                    bid_vol = f"{row['bid_volume1']:,}股"
                    result.append(f"📥 委托买盘: {bid_vol}")
                
                result.append("")
        else:
            # 列表模式：表格显示
            headers = ["股票代码", "股票名称", "最新价", "昨收价", "涨跌额", "涨跌幅%", "最高价", "最低价", "成交量"]
            result.append(" | ".join([f"{h:^10}" for h in headers]))
            result.append("-" * (12 * len(headers)))
            
            for _, row in df.head(50).iterrows():  # 限制显示前50条
                ts_code_display = row['ts_code']
                name = row['name'][:6] if len(str(row['name'])) > 6 else str(row['name'])  # 限制名称长度
                
                close_price = f"{row['close']:.2f}" if pd.notna(row['close']) else '-'
                pre_close = f"{row['pre_close']:.2f}" if pd.notna(row['pre_close']) else '-'
                high_price = f"{row['high']:.2f}" if pd.notna(row['high']) else '-'
                low_price = f"{row['low']:.2f}" if pd.notna(row['low']) else '-'
                
                # 计算涨跌
                if pd.notna(row['close']) and pd.notna(row['pre_close']):
                    change = row['close'] - row['pre_close']
                    pct_chg = (change / row['pre_close']) * 100
                    change_str = f"{change:+.2f}"
                    pct_chg_str = f"{pct_chg:+.2f}"
                else:
                    change_str = "-"
                    pct_chg_str = "-"
                
                # 成交量格式化
                if pd.notna(row['vol']):
                    vol_display = f"{row['vol']//10000:.0f}万" if row['vol'] >= 10000 else f"{row['vol']:.0f}"
                else:
                    vol_display = "-"
                
                data_row = [ts_code_display, name, close_price, pre_close, 
                           change_str, pct_chg_str, high_price, low_price, vol_display]
                result.append(" | ".join([f"{d:^10}" for d in data_row]))
            
            if len(df) > 50:
                result.append(f"\n... 还有{len(df)-50}条数据未显示 ...")
        
        # 市场统计
        if len(df) > 1:
            result.append("\n📊 市场统计")
            result.append("-" * 20)
            
            # 涨跌统计
            if 'pct_chg' in df.columns:
                up_count = len(df[df['pct_chg'] > 0])
                down_count = len(df[df['pct_chg'] < 0])
                flat_count = len(df[df['pct_chg'] == 0])
                
                result.append(f"🔴 上涨: {up_count}只")
                result.append(f"🟢 下跌: {down_count}只")
                result.append(f"⚪ 平盘: {flat_count}只")
                
                if len(df[df['pct_chg'].notna()]) > 0:
                    avg_pct_chg = df['pct_chg'].mean()
                    result.append(f"📈 平均涨跌幅: {avg_pct_chg:.2f}%")
            
            # 成交统计
            if 'vol' in df.columns and df['vol'].notna().any():
                total_vol = df['vol'].sum()
                result.append(f"💹 总成交量: {total_vol:,.0f}股")
                
            if 'amount' in df.columns and df['amount'].notna().any():
                total_amount = df['amount'].sum()
                result.append(f"💰 总成交额: {total_amount:,.0f}元")
        
        result.append("\n⚠️ 数据说明")
        result.append("-" * 20)
        result.append("• 数据为实时日K线行情")
        result.append("• 显示当日开盘以来累计数据")
        result.append("• 成交量单位：股")
        result.append("• 成交额单位：元")
        result.append("• 支持通配符查询（如6*.SH）")
        result.append("• 单次最大可提取6000条数据")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"查询失败：{str(e)}\n\n请检查：\n1. 股票代码格式是否正确（必须带.SH/.SZ/.BJ后缀）\n2. 是否有访问实时数据的权限\n3. 网络连接是否正常"

@mcp.tool()
def get_daily_stock_price(
    ts_code: str = "",
    trade_date: str = "",
    start_date: str = "",
    end_date: str = ""
) -> str:
    """
    获取A股日线行情数据
    
    参数:
        ts_code: 股票代码，支持多个股票同时提取，逗号分隔（如：000001.SZ,600000.SH）
        trade_date: 交易日期（YYYYMMDD格式，如：20240801）
        start_date: 开始日期（YYYYMMDD格式，如：20240701）
        end_date: 结束日期（YYYYMMDD格式，如：20240731）
    """
    if not get_tushare_token():
        return "请先配置Tushare token"
    
    try:
        pro = ts.pro_api()
        
        # 构建查询参数
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        # 如果没有提供任何参数，返回提示
        if not any(params.values()):
            return "请至少提供一个查询参数：股票代码、交易日期或日期范围"
            
        df = pro.daily(**params)
        
        if df.empty:
            return "未找到符合条件的行情数据"
            
        # 按交易日期和股票代码排序
        df = df.sort_values(['ts_code', 'trade_date'])
        
        # 格式化输出
        result = []
        result.append("📈 A股日线行情数据")
        result.append("=" * 60)
        
        # 按股票分组显示
        for ts_code_group in df['ts_code'].unique():
            stock_data = df[df['ts_code'] == ts_code_group]
            
            # 获取股票名称
            try:
                stock_info = pro.stock_basic(ts_code=ts_code_group)
                stock_name = stock_info.iloc[0]['name'] if not stock_info.empty else ts_code_group
            except:
                stock_name = ts_code_group
                
            result.append(f"\n🏢 {stock_name}（{ts_code_group}）")
            result.append("-" * 50)
            
            # 表头
            headers = ["交易日期", "开盘价", "最高价", "最低价", "收盘价", "昨收价", "涨跌额", "涨跌幅%", "成交量(手)", "成交额(千元)"]
            result.append(" | ".join([f"{h:^10}" for h in headers]))
            result.append("-" * (12 * len(headers)))
            
            # 数据行
            for _, row in stock_data.iterrows():
                trade_date = row['trade_date']
                open_price = f"{row['open']:.2f}" if pd.notna(row['open']) else '-'
                high_price = f"{row['high']:.2f}" if pd.notna(row['high']) else '-'
                low_price = f"{row['low']:.2f}" if pd.notna(row['low']) else '-'
                close_price = f"{row['close']:.2f}" if pd.notna(row['close']) else '-'
                pre_close = f"{row['pre_close']:.2f}" if pd.notna(row['pre_close']) else '-'
                change = f"{row['change']:+.2f}" if pd.notna(row['change']) else '-'
                pct_chg = f"{row['pct_chg']:+.2f}" if pd.notna(row['pct_chg']) else '-'
                vol = f"{row['vol']:,.0f}" if pd.notna(row['vol']) else '-'
                amount = f"{row['amount']:,.0f}" if pd.notna(row['amount']) else '-'
                
                data_row = [trade_date, open_price, high_price, low_price, close_price, 
                           pre_close, change, pct_chg, vol, amount]
                result.append(" | ".join([f"{d:^10}" for d in data_row]))
            
            # 统计分析
            if len(stock_data) > 1:
                result.append("\n📊 统计分析")
                result.append("-" * 20)
                
                latest = stock_data.iloc[-1]
                first = stock_data.iloc[0]
                
                # 期间涨跌幅
                if pd.notna(latest['close']) and pd.notna(first['close']):
                    period_return = ((latest['close'] - first['close']) / first['close']) * 100
                    result.append(f"• 期间涨跌幅：{period_return:+.2f}%")
                
                # 最高最低价
                max_high = stock_data['high'].max()
                min_low = stock_data['low'].min()
                result.append(f"• 期间最高价：{max_high:.2f}")
                result.append(f"• 期间最低价：{min_low:.2f}")
                
                # 平均成交量和成交额
                avg_vol = stock_data['vol'].mean()
                avg_amount = stock_data['amount'].mean()
                result.append(f"• 平均成交量：{avg_vol:,.0f}手")
                result.append(f"• 平均成交额：{avg_amount:,.0f}千元")
                
                # 波动率
                if len(stock_data) > 1:
                    volatility = stock_data['pct_chg'].std()
                    result.append(f"• 日收益率标准差：{volatility:.2f}%")
        
        result.append("\n⚠️ 数据说明")
        result.append("-" * 20)
        result.append("• 本接口提供未复权行情数据")
        result.append("• 停牌期间不提供数据")
        result.append("• 交易日每天15点~16点之间更新")
        result.append("• 涨跌幅基于除权后的昨收价计算")
        result.append("• 成交量单位：手（1手=100股）")
        result.append("• 成交额单位：千元")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"查询失败：{str(e)}"

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