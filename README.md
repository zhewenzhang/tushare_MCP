[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/zhewenzhang-tushare-mcp-badge.png)](https://mseep.ai/app/zhewenzhang-tushare-mcp)

# Tushare MCP Server

基于 MCP (Model Context Protocol) 的 Tushare 金融数据服务器，提供 52 个专业金融数据分析工具。

## 🎯 项目特性

- ✅ **52个专业工具** - 涵盖股票、期货、外汇、财务等10大类
- ✅ **双模式支持** - stdio 模式和 HTTP SSE 模式
- ✅ **智能缓存** - 自动缓存管理，提升查询效率
- ✅ **权限管理** - 支持不同 Tushare 权限级别
- ✅ **开箱即用** - 自动工具发现和注册

## 📦 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Tushare Token

在项目根目录创建 `.env` 文件：

```env
TUSHARE_TOKEN=your_token_here
```

获取 Token: [https://tushare.pro/user/token](https://tushare.pro/user/token)

### 3. 选择运行模式

#### 方式 A: stdio 模式（推荐用于 Claude Desktop）

**配置文件**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) 或 `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "tushare": {
      "command": "python",
      "args": ["D:/AI/tushare_MCP/server.py"]
    }
  }
}
```

**启动**: 重启 Claude Desktop 即可自动启动

#### 方式 B: Streamable HTTP 模式（推荐用于调试和远程访问）

**启动服务器**:
```bash
# Windows
start_http_server.bat

# Linux/macOS
chmod +x start_http_server.sh
./start_http_server.sh
```

**配置文件**: 同上 Claude Desktop 配置文件

```json
{
  "mcpServers": {
    "tushare-http": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```



## 🛠️ 模式对比

| 特性 | stdio 模式 | Streamable HTTP 模式 |
|------|-----------|--------------|
| **通信方式** | 标准输入输出 | HTTP JSON-RPC |
| **网络访问** | ❌ 仅本地进程 | ✅ 支持网络访问 |
| **并发连接** | ❌ 单客户端 | ✅ 多客户端 |
| **调试难度** | 🔴 较难 | 🟢 容易（可用 curl 测试） |
| **适用场景** | 本地单用户 | 开发调试、多用户、远程访问 |
| **配置方式** | `command` + `args` | `url` |

## 📊 工具分类

Tushare MCP 工具完整列表
本文档列出了所有支持的MCP工具，共 52个工具，分为10个类别。

📊 一、Alpha策略分析工具 (6个)
行业Alpha分析
analyze_sector_alpha_strategy

功能：分析单个板块相对强度Alpha，计算2日和5日Alpha收益
参数：sector_code（板块代码，必填）、benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）
说明：计算2天和5天的区间收益率，计算超额收益Alpha = 板块收益 - 基准收益，综合得分 = Alpha_2 × 60% + Alpha_5 × 40%
rank_sectors_by_alpha

功能：申万一级行业Alpha排名，显示前N名强势板块
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）、top_n（显示前N名，默认10）
说明：自动分析所有31个申万一级行业，按综合得分降序排列
rank_l2_sectors_by_alpha

功能：申万二级行业Alpha排名，显示前N名强势板块
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）、top_n（显示前N名，默认20）
说明：自动分析所有已发布指数的申万二级行业，按综合得分降序排列
rank_l1_sectors_alpha_full

功能：申万一级行业Alpha综合得分完整排行（所有31个行业）
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）
说明：显示所有申万一级行业的完整排名
rank_l1_sectors_alpha_velocity

功能：申万一级行业Alpha排名上升速度分析
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）
说明：计算排名上升速度（当天对比前一天和前两天的排名变化），正数表示排名上升，负数表示排名下降
rank_l2_sectors_alpha_velocity

功能：申万二级行业Alpha排名上升速度分析
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）、top_n（显示前N名，默认20）
说明：计算排名上升速度，包括一天内上升位数排行和两天内上升位数排行
📈 二、股票行情工具 (22个)
股票基本信息
get_stock_basic_info

功能：获取股票基本信息（代码、名称、上市日期、行业等）
参数：ts_code（股票代码，如：000001.SZ）或 name（股票名称，如：平安银行）
说明：支持通过代码或名称查询
search_stocks

功能：搜索股票，支持代码或名称模糊匹配
参数：keyword（关键词，必填，可以是股票代码的一部分或股票名称的一部分）
说明：支持模糊搜索，返回匹配的股票列表
股票行情数据
get_stock_daily

功能：获取A股日线行情（开盘、收盘、最高、最低、成交量等）
参数：ts_code（股票代码，支持多个，逗号分隔）、trade_date（交易日期，YYYYMMDD格式）、start_date/end_date（日期范围，YYYYMMDD格式）
说明：支持单只股票或批量查询，支持单日或日期范围查询，交易日每天15点～16点之间入库，本接口是未复权行情
get_stock_weekly

功能：获取A股周线行情，支持单只股票或批量查询
参数：ts_code（股票代码，必填，支持多个，逗号分隔）、trade_date（交易日期，YYYYMMDD格式）、start_date/end_date（日期范围，YYYYMMDD格式）
说明：trade_date为该周的最后交易日（通常是周五），周线数据每周更新一次，本接口是未复权行情
get_stock_min

功能：获取A股实时分钟行情数据
参数：ts_code（股票代码，必填，如：600000.SH，支持多个股票，逗号分隔）、freq（分钟频度，必填，默认1MIN：1MIN/5MIN/15MIN/30MIN/60MIN）、date_str（回放日期，可选，格式：YYYY-MM-DD，默认为交易当日，支持回溯一天）
说明：数据来源Tushare rt_min接口（实时）或rt_min_daily接口（历史回放），支持1min/5min/15min/30min/60min行情，显示开盘、最高、最低、收盘、成交量、成交额等数据，需单独开权限，单次最大1000行数据，支持多个股票同时提取，注意：rt_min_daily接口仅支持单个股票提取
get_stock_rt_k

功能：获取沪深京实时日线行情数据
参数：ts_code（股票代码，必填，支持通配符方式：单个股票如600000.SH、000001.SZ、430047.BJ，通配符如6*.SH、301*.SZ、0*.SZ、9*.BJ，多个股票或通配符如600000.SH,000001.SZ，代码必须带.SH/.SZ/.BJ后缀）
说明：数据来源Tushare rt_k接口，获取实时日k线行情，支持按股票代码及股票代码通配符一次性提取全部股票实时日k线行情，显示开盘、最高、最低、收盘（最新价）、成交量、成交金额、成交笔数、委托买卖盘等数据，本接口是单独开权限的数据，单次最大可提取6000条数据，等同于一次提取全市场，注意：不建议一次提取全市场，可分批提取性能更好
ETF基金
get_etf_daily
功能：获取ETF日线行情数据，支持单只ETF或批量查询
参数：ts_code（ETF基金代码，支持多个，逗号分隔）、trade_date（交易日期，YYYYMMDD格式）、start_date/end_date（日期范围，YYYYMMDD格式）
说明：常用ETF代码：510330.SH（沪深300ETF华夏）、510300.SH（沪深300ETF）、159919.SZ（沪深300ETF），获取ETF行情每日收盘后成交数据，历史超过10年，单次最大2000行记录
A股指数
get_index_daily
功能：获取A股指数日线行情（沪深300、上证指数、深证成指等）
参数：ts_code（指数代码，支持多个，逗号分隔）、trade_date（交易日期，YYYYMMDD格式）、start_date/end_date（日期范围，YYYYMMDD格式）
说明：常用指数代码：000300.SH（沪深300）、000001.SH（上证指数）、399001.SZ（深证成指）、399006.SZ（创业板指），交易日每天15点～16点之间入库，本接口是未复权行情
限售股解禁数据
get_share_float
功能：获取限售股解禁数据
参数：ts_code（股票代码，如：000998.SZ，可选）、ann_date（公告日期，YYYYMMDD格式，可选）、float_date（解禁日期，YYYYMMDD格式，可选）、start_date/end_date（解禁日期范围，YYYYMMDD格式，可选）
说明：数据来源Tushare share_float接口，支持按股票代码、公告日期、解禁日期、日期范围筛选，显示解禁日期、流通股份、流通股份占总股本比率、股东名称、股份类型等信息，需要2000积分权限
股票回购数据
get_stock_repurchase
功能：获取上市公司股票回购数据
参数：ann_date（公告日期，YYYYMMDD格式，如：20181010，可选）、start_date/end_date（公告日期范围，YYYYMMDD格式，可选）
说明：数据来源Tushare repurchase接口，支持按公告日期、日期范围筛选，显示公告日期、截止日期、进度、过期日期、回购数量、回购金额、回购最高价、回购最低价等信息，需要600积分权限，注意：如果都不填参数，单次默认返回2000条数据
股权质押数据
get_pledge_detail
功能：获取股票股权质押明细数据
参数：ts_code（股票代码，必填，如：000014.SZ）
说明：数据来源Tushare pledge_detail接口，显示股票质押明细数据，包括公告日期、股东名称、质押数量、质押开始/结束日期、是否已解押、解押日期、质押方、持股总数、质押总数、质押比例等信息，需要500积分权限，单次最大可调取1000条数据
大宗交易数据
get_block_trade
功能：获取大宗交易数据
参数：ts_code（股票代码，如：600436.SH，可选）、trade_date（交易日期，YYYYMMDD格式，如：20181227，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源Tushare block_trade接口，支持按股票代码、交易日期、日期范围筛选，显示交易日期、成交价、成交量、成交金额、买方营业部、卖方营业部等信息，权限要求请查看Tushare文档确认
公告信号扫描
scan_announcement_signals
功能：扫描上市公司公告标题，捕捉【重大利好】或【重大利空】信号
参数：ts_code_list（股票代码列表，多个代码用逗号分隔，如：000001.SZ,600000.SH，可选，若为空则扫描全市场）、check_date（公告日期，YYYYMMDD格式，如：20230621，可选，默认当天）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源Tushare anns_d接口，根据公告标题关键词自动分类为：利好催化、利空警报、重大事项，支持按股票代码列表和日期筛选，权限要求：本接口为单独权限，请参考Tushare权限说明，限量：单次最大2000条数据，可以按日期循环获取全量
股东数据
get_stock_holder_trade

功能：获取上市公司股东增减持数据
参数：ts_code（股票代码，可选）、ann_date（公告日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、trade_type（交易类型：IN增持/DE减持，可选）、holder_type（股东类型：C公司/P个人/G高管，可选）
说明：数据来源于上市公司公告，显示增减持数量、占流通比例、平均价格等信息，至少需要提供一个查询条件
get_stock_holder_number

功能：获取上市公司股东户数数据
参数：ts_code（股票代码，可选）、ann_date（公告日期，YYYYMMDD格式，可选）、enddate（截止日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源于上市公司定期报告，不定期公布，股东户数变化可以反映股票的集中度变化趋势，至少需要提供一个查询条件
机构调研数据
get_stock_survey
功能：获取上市公司机构调研记录数据
参数：ts_code（股票代码，可选）、trade_date（调研日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源于上市公司披露的机构调研记录，显示机构参与人员、接待地点、接待方式、接待公司等信息，需要5000积分权限，单次最大获取100条数据，至少需要提供一个查询条件
筹码分析数据
get_cyq_perf
功能：获取A股每日筹码平均成本和胜率情况
参数：ts_code（股票代码，必填）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据每天17~18点左右更新，从2018年开始，自动计算筹码集中度，需要5000积分权限，单次最大5000条数据，筹码集中度计算公式：集中度 = (cost_95pct - cost_5pct) / (cost_95pct + cost_5pct)，集中度越小，说明筹码越集中；集中度越大，说明筹码越分散
融资融券数据
get_margin

功能：获取融资融券每日交易汇总数据（按交易所）
参数：trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、exchange_id（交易所代码：SSE上交所/SZSE深交所/BSE北交所，可选）
说明：数据来源于证券交易所网站，提供融资余额、融资买入额、融资偿还额、融券余额等汇总数据，需要2000积分权限，单次请求最大返回4000行数据
get_margin_detail

功能：获取融资融券交易明细数据（按股票代码）
参数：ts_code（股票代码，支持多个，逗号分隔，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源于证券公司报送的融资融券余额数据，提供每只股票的融资融券明细数据，需要2000积分权限，单次请求最大返回4000行数据，至少需要提供一个查询条件
资金流向数据
get_stock_moneyflow_dc
功能：获取东方财富个股资金流向数据
参数：ts_code（股票代码，留空则查询所有股票，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源东方财富，每日盘后更新，数据开始于20230911，显示主力净流入额、超大单/大单/中单/小单的净流入额和占比，需要5000积分权限，单次最大获取6000条数据，至少需要提供一个查询条件
每日指标数据
get_daily_basic
功能：获取每日指标数据（估值指标、换手率、量比、市值等）
参数：ts_code（股票代码，支持多个，逗号分隔，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：包括估值指标（PE、PB、PS）、换手率、量比、总市值、流通市值等，支持按股票代码、交易日期、日期范围查询，至少需要提供一个查询条件
龙虎榜数据
get_top_list

功能：获取龙虎榜每日交易明细数据
参数：trade_date（交易日期，必填，YYYYMMDD格式）、ts_code（股票代码，可选）
说明：数据来源Tushare top_list接口，数据历史2005年至今，显示收盘价、涨跌幅、换手率、总成交额、龙虎榜买入/卖出额、净买入额、上榜理由等，需要2000积分权限，单次最大10000行数据
get_top_inst

功能：获取龙虎榜机构成交明细数据
参数：trade_date（交易日期，必填，YYYYMMDD格式）、ts_code（股票代码，可选）
说明：数据来源Tushare top_inst接口，显示营业部名称、买卖类型（0买入金额最大的前5名/1卖出金额最大的前5名）、买入额、卖出额、净成交额、买入/卖出占比、上榜理由等，需要5000积分权限，单次最大10000行数据
📊 三、指数行情工具 (4个)
国际指数
get_global_index

功能：获取国际主要指数行情（道琼斯、标普500、纳斯达克等）
参数：index_code（指数代码，如：XIN9、HSI、DJI、SPX、IXIC等，可选）、index_name（指数名称，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：支持20多个国际主要指数，包括富时中国A50、恒生指数、道琼斯、标普500、纳斯达克、日经225等，至少需要提供一个查询条件
search_global_indexes

功能：搜索可用国际指数，支持关键词筛选
参数：keyword（搜索关键词，可选，留空则显示所有可用指数）
说明：返回所有支持的国际指数列表，或根据关键词筛选
行业指数
get_sw_industry_daily

功能：获取申万行业指数日线行情（一级、二级、三级行业）
参数：ts_code（指数代码，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、level（行业分级：L1/L2/L3，默认L1）
说明：L1为一级行业（如：采掘、化工、钢铁等），L2为二级行业，L3为三级行业，交易日每天15点～16点之间入库，本接口是未复权行情，至少需要提供一个查询条件
get_industry_index_codes

功能：获取申万行业分类指数代码列表（L1/L2/L3）
参数：level（行业分级：L1/L2/L3，默认L1）、src（指数来源：SW2014/SW2021，默认SW2021）
说明：返回申万行业分类的指数代码列表，包括指数代码、行业名称、行业代码等信息
💱 四、外汇工具 (1个)
get_fx_daily
功能：获取外汇日线行情（美元人民币、欧元美元等交易对）
参数：ts_code（交易对代码，支持多个，逗号分隔，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：常用交易对代码：USDCNH.FXCM（美元人民币）、EURUSD.FXCM（欧元美元）、GBPUSD.FXCM（英镑美元）、USDJPY.FXCM（美元日元），至少需要提供交易对代码(ts_code)或交易日期(trade_date)之一
📈 五、期货工具 (5个)
get_fut_basic

功能：获取期货合约基本信息
参数：exchange（交易所代码，必填：CFFEX中金所/DCE大商所/CZCE郑商所/SHFE上期所/INE上海国际能源交易中心/GFEX广州期货交易所）、fut_type（合约类型：1普通合约/2主力与连续合约，可选）、fut_code（标准合约代码，如：AG、AP等，可选）、list_date（上市开始日期，YYYYMMDD格式，可选）
说明：显示合约代码、交易标识、交易市场、中文简称、合约产品代码、合约乘数、交易单位、报价单位、上市日期、最后交易日期、交割月份、最后交割日等信息
get_nh_index

功能：获取南华期货指数日线行情数据
参数：ts_code（指数代码，支持多个，逗号分隔，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：数据来源Tushare index_daily接口，显示开盘、最高、最低、收盘、涨跌点、涨跌幅、成交量、成交额等行情数据，需要2000积分权限，常用指数：NHCI.NH(南华商品指数)、NHAI.NH(南华农产品指数)、CU.NH(南华沪铜指数)、AU.NH(南华沪黄金指数)等，至少需要提供一个查询条件
get_fut_holding

功能：获取期货每日持仓排名数据
参数：trade_date（交易日期，YYYYMMDD格式，可选）、symbol（合约或产品代码，如：C1905、C等，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、exchange（交易所代码，可选：CFFEX/DCE/CZCE/SHFE/INE/GFEX）
说明：数据来源Tushare fut_holding接口，显示期货公司会员的成交量、成交量变化、持买仓量、持买仓量变化、持卖仓量、持卖仓量变化等数据，需要2000积分权限，单次最大可调取5000条数据，至少需要提供交易日期(trade_date)或日期范围(start_date/end_date)之一
get_fut_wsr

功能：获取期货仓单日报数据
参数：trade_date（交易日期，YYYYMMDD格式，可选）、symbol（产品代码，如：ZN锌、CU铜等，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、exchange（交易所代码，可选：CFFEX/DCE/CZCE/SHFE/INE/GFEX）
说明：数据来源Tushare fut_wsr接口，显示各仓库/厂库的仓单变化情况，包括昨日仓单量、今日仓单量、增减量等信息，需要2000积分权限，单次最大可调取1000条数据，至少需要提供交易日期(trade_date)或日期范围(start_date/end_date)之一
get_fut_min

功能：获取期货实时分钟行情数据
参数：ts_code（期货合约代码，必填，如：CU2501.SHF，支持多个合约，逗号分隔）、freq（分钟频度，必填，默认1MIN：1MIN/5MIN/15MIN/30MIN/60MIN）、date_str（回放日期，可选，格式：YYYY-MM-DD，默认为交易当日，支持回溯一天）
说明：数据来源Tushare rt_fut_min接口（实时）或rt_fut_min_daily接口（历史回放），支持1min/5min/15min/30min/60min行情，显示开盘、最高、最低、收盘、成交量、成交金额、持仓量等数据，需单独开权限，每分钟可以请求500次，支持多个合约同时提取
📋 六、财务报表工具 (2个)
get_income_statement

功能：获取利润表数据，支持合并报表和母公司报表
参数：ts_code（股票代码，必填）、start_date（开始日期，YYYYMMDD格式，可选）、end_date（结束日期，YYYYMMDD格式，可选）、report_type（报告类型，默认1合并报表，可选值：1-12）
说明：支持12种报告类型，包括合并报表、单季合并、母公司报表等
get_fina_indicator

功能：获取财务指标数据（盈利能力、成长能力、运营能力、偿债能力等）
参数：ts_code（股票代码，可选）、ann_date（公告日期，YYYYMMDD格式，可选）、start_date/end_date（报告期日期范围，YYYYMMDD格式，可选）、period（报告期，可选）
说明：数据来源于上市公司定期报告，每年发布4次（一季报、半年报、三季报、年报），包含ROE、ROA、毛利率、净利率、资产负债率、周转率等各类财务指标，至少需要提供一个查询条件
📊 七、概念板块工具 (8个)
概念板块数据
get_eastmoney_concept_board

功能：获取东方财富概念板块行情数据
参数：ts_code（指数代码，支持多个，逗号分隔，如：BK1186.DC,BK1185.DC，可选）、name（板块名称，例如：人形机器人，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）
说明：需要6000积分权限，返回概念代码、概念名称、涨跌幅、领涨股票、总市值、换手率等，单次最大可获取5000条数据，至少需要提供一个查询条件
get_eastmoney_concept_member

功能：获取东方财富板块每日成分数据
参数：ts_code（板块指数代码，如：BK1184.DC人形机器人，可选）、con_code（成分股票代码，如：002117.SZ，可选）、trade_date（交易日期，YYYYMMDD格式，可选）
说明：可以根据概念板块代码和交易日期，获取历史成分；也可以查询某只股票属于哪些概念板块，需要6000积分权限，单次最大获取5000条数据，至少需要提供一个查询条件
get_eastmoney_concept_daily

功能：获取东财概念板块、行业指数板块、地域板块行情数据
参数：ts_code（板块代码，格式：xxxxx.DC，如：BK1184.DC，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、idx_type（板块类型：概念板块/行业板块/地域板块，可选）
说明：历史数据开始于2020年，单次最大2000条数据，需要6000积分权限，至少需要提供一个查询条件
概念板块Alpha分析
analyze_concept_alpha_strategy

功能：分析单个东财概念板块的相对强度Alpha
参数：concept_code（概念板块代码，必填，如：BK1184.DC人形机器人、BK1186.DC首发经济等）、benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）
说明：计算2天和5天的区间收益率，计算超额收益Alpha，综合得分 = Alpha_2 × 60% + Alpha_5 × 40%
rank_concepts_by_alpha

功能：概念板块Alpha排名，计算相对沪深300的超额收益
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）、top_n（显示前N名，默认20）、hot_limit（筛选的热门概念板块数量，默认80，根据成交额和换手率筛选）
说明：自动获取指定日期的热门概念板块（根据成交额和换手率筛选），按综合得分降序排列，显示前N名强势板块，仅分析热门板块以减少计算量，提高响应速度
rank_concepts_alpha_velocity

功能：概念板块Alpha排名上升速度，识别快速上升概念
参数：benchmark_code（基准指数，默认000300.SH）、end_date（结束日期，YYYYMMDD格式，默认今天）
说明：计算排名上升速度（当天对比前一天和前两天的排名变化），正数表示排名上升，负数表示排名下降
板块资金流向
get_concept_moneyflow_dc
功能：获取东方财富板块资金流向数据（概念、行业、地域）
参数：ts_code（板块代码，如：BK1184.DC，留空则查询所有板块，可选）、trade_date（交易日期，YYYYMMDD格式，可选）、start_date/end_date（日期范围，YYYYMMDD格式，可选）、content_type（资金类型：行业/概念/地域，留空则查询所有类型，可选）
说明：数据来源东方财富，每天盘后更新，显示主力净流入额、超大单/大单/中单/小单的净流入额和占比、主力净流入最大股、排名等信息，需要5000积分权限，单次最大可调取5000条数据，至少需要提供一个查询条件
概念板块成交量异动
scan_concepts_volume_anomaly
功能：分析东财概念板块成交量异动
参数：end_date（结束日期，YYYYMMDD格式，默认今天，可选）、vol_ratio_threshold（成交量比率阈值，默认1.15，即MA3/MA10 > 1.15，资金进场）、price_change_5d_min（5日涨幅最小值，默认0.02，即2%，右侧启动）、price_change_5d_max（5日涨幅最大值，默认0.08，即8%，拒绝左侧死鱼）、hot_limit（扫描的热门概念板块数量，默认160，根据成交额和换手率筛选）
说明：扫描热门东财概念板块（根据成交额和换手率筛选），计算指标：Volume_Ratio = MA3_Vol / MA10_Vol、Price_Change_5d（5日涨幅）、Turnover_Rate（换手率），筛选逻辑：Volume_Ratio > vol_ratio_threshold（资金进场）且 price_change_5d_min < Price_Change_5d < price_change_5d_max（右侧启动），返回JSON格式字符串
📊 八、成交量异动分析工具 (1个)
scan_l2_volume_anomaly
功能：扫描申万二级行业成交量异动，识别量价背离信号
参数：end_date（结束日期，YYYYMMDD格式，默认今天，可选）、vol_ma_short（成交量短期MA天数，默认3，即MA3，可设置为1、3、5等）、vol_ma_long（成交量长期MA天数，默认10，即MA10，可设置为3、5、10、20等）、vol_ratio_threshold（成交量比率阈值，默认1.5，即MA短/MA长 > 1.5）、price_change_5d_threshold（5日涨幅阈值，默认0.03，即3%）
说明：筛选条件：(成交量MA短/成交量MA长) > 阈值 且 近5日涨幅 < 阈值，根据价格位置判断信号类型（高位>70%分位：出货信号Distribution，低位<30%分位或均线之上：潜伏信号Accumulation，其他：待确认Uncertain），返回JSON格式字符串
🗄️ 九、缓存管理工具 (1个)
get_cache_stats
功能：获取缓存统计信息（缓存数量、访问次数等）
参数：无
说明：显示所有缓存类型的统计信息，包括缓存数量和访问次数
📝 使用说明
日期格式
所有日期参数格式：YYYYMMDD（如：20250102）
如果未提供日期，默认使用今天
回放日期格式：YYYY-MM-DD（如：2025-01-02）
基准指数
Alpha分析默认基准指数：000300.SH（沪深300）
可以自定义基准指数代码
数据来源
概念板块数据：东方财富（需要6000积分权限）
行业数据：Tushare（申万行业分类）
股票数据：Tushare
国际指数：Tushare
期货数据：Tushare
缓存机制
所有工具支持缓存，提高查询效率
缓存数据永久保留，过期后标记状态
可以使用 get_cache_stats 查看缓存统计
权限要求
大部分工具需要基础Tushare权限
2000积分权限工具：
get_nh_index（南华期货指数）
get_margin（融资融券汇总）
get_margin_detail（融资融券明细）
get_top_list（龙虎榜每日明细）
get_fut_holding（期货持仓排名）
get_fut_wsr（期货仓单日报）
get_share_float（限售股解禁）
5000积分权限工具：
get_stock_survey（机构调研）
get_cyq_perf（筹码分析）
get_stock_moneyflow_dc（个股资金流向）
get_concept_moneyflow_dc（板块资金流向）
get_top_inst（龙虎榜机构明细）
6000积分权限工具：
get_eastmoney_concept_board（东财概念板块）
get_eastmoney_concept_daily（东财概念行情）
get_eastmoney_concept_member（东财概念成分）
单独权限工具（需单独申请）：
get_stock_min（A股实时分钟行情）
get_stock_rt_k（沪深京实时日线）
get_fut_min（期货实时分钟行情）
scan_announcement_signals（公告信号扫描）
📊 工具统计
总工具数：52个
Alpha策略分析：6个
股票行情工具：22个
指数行情工具：4个
外汇工具：1个
期货工具：5个
财务报表工具：2个
概念板块工具：8个
成交量异动分析：1个
缓存管理工具：1个

统计分时线的脚本
python g:\AICode\tocker-mcp\tushare_MCP\scripts\realtime_collector.py

统计板块强度的脚本
python g:\AICode\tocker-mcp\tushare_MCP\scripts\sector_strength_collector.py


analyze_sector_health: 新增板块健康度分析工具。它通过对过去一小时的板块评分进行线性回归，计算趋势斜率（Slope），并结合成交量连贯性和内生广度（上涨占比），对板块走势的可持续性进行 A/B/C 评级。
get_index_rt_k: 基于你提供的 rt_k API 文献实现。专用于获取指数（如 000001.SH 上证指数）的实时日线快照，方便作为相对强度的基准。
scan_realtime_strong_sectors: 优化了实时强度扫描逻辑，现在会自动抓取全市场行情（6字头、0字头、3字头、北交所等通配符），并更精确地与昨日同刻成交量进行对比。