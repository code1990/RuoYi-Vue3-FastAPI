# 数据表字典

本文件描述 `config.get_db_path()` 指向的 SQLite 数据库业务表。近期新增的单股票爬虫已用 `000001` 手工低频验证；接口无数据时表可能存在但行数为 0。

- 所有证券标识统一使用 `stock_code`。
- 金额、比例、数量中标注为 `TEXT` 的字段保留接口原始精度，使用时再转换为数值。
- `*_json` 虽是 `TEXT` 列，但内容必须是合法 JSON；具体格式见“JSON 字段”章节。
- 行数是动态数据，不写入本字典；可用 `SELECT COUNT(*) FROM 表名` 检查。

## 基础行情与股票池

| 表 | 作用 | 主键/关键字段 |
|---|---|---|
| `t_stock_pool` | A 股股票池和分类元数据 | `code`、`stock_code`、`stock_name`、`market_code`、`stock_type`、行业/概念字段、`capital`、`price` |
| `t_stock_daily_240` | 日 K 历史行情 | 唯一键 `(stock_code, trade_date)`；开高低收、`vol`、`amount`、涨跌幅、前收 |
| `t_stock_daily_60` | 60 分钟历史行情 | 唯一键 `(stock_code, trade_time)`；`trade_date`、开高低收、成交量额、涨跌幅 |
| `t_stock_daily_15` | 15 分钟历史行情 | 唯一键 `(stock_code, trade_time)`；开高低收、成交量额、涨跌幅，供三周期交易信号计算 |
| `t_stock_daily_5` | 5 分钟历史行情 | 唯一键 `(stock_code, trade_time)`；开高低收、成交量额、涨跌幅，供回踩与止损信号计算 |
| `t_stock_daily_30min_history` | 早盘 30 分钟回测行情 | 唯一键 `(stock_code, trade_date)`；每天只保留最早一根 30 分钟 K，`trade_date` 与日线对齐 |
| `t_stock_daily_5min_history` | 当天 09:35 快照恢复 | 唯一键 `(stock_code, trade_date)`；只写当天 `09:35` K，不回补历史 |
| `t_stock_single_kline` | 同花顺前复权日 K 线补充数据源 | 唯一键 `(stock_code, trade_date)`；`stock_name`、开高低收、`vol`、`amount` |
| `t_stock_quote` | 盘中行情快照 | `stock_code`、`data_timestamp`、`market_date`、`close_px`、`amount`、`turnover_ratio`、买卖盘组 |
| `t_stock_index_quote` | 指数日内快照 | 主键 `(stock_code, market_date)`；各分类指数的接口原始字段，缺失接口日期时用上海时区采集日 |
| `t_future_product` | 期货品种元数据 | 主键 `(market_code, product_code)`；名称、精度和交易时段 JSON；市场列表内置脚本，不单独建表 |
| `t_future_quote` | 期货合约行情 | 主键 `(stock_code, market_date, quote_timestamp)`；`/sort` 返回的原始行情字段，按合约时间戳追加 |
| `t_fund_quote` | 沪深基金快照 | 主键 `(stock_code, market_date)`；ETF、LOF、分级和封闭式基金的接口原始行情字段 |
| `t_bond_quote` | 沪深债券快照 | 主键 `(stock_code, market_date)`；债券、转债价格、收益率、久期和买卖盘等接口原始字段 |
| `t_hk_stock_quote` | 港股主板和创业板快照 | 主键 `(stock_code, market_date)`；价格、估值、买卖盘、行权与发行字段等接口原始行情 |
| `t_stock_margin_trading` | A 股融资融券日快照 | 主键 `(stock_code, trade_date)`；融资/融券发生额、余额、偿还额/量、增速及价格涨跌 |
| `t_stock_margin_rank_performance` | 两融多空 Top 30 跟踪 | 主键 `(margin_trade_date, side, rank_no)`；保存排名、强度组成、T+1 开盘入场价和收盘表现、T+2~T+3 可卖窗口最高收益及夜报发送标记 |
| `t_stock_dde_fund_flow` | iWenCai DDE 资金流快照 | 主键 `(stock_code, trade_date, snapshot_slot)`；早盘/午盘/尾盘及 `post_close` 盘后研究快照的特大单、大单、中单、小单、市值、成交额、涨跌幅和最新价原值 |
| `t_stock_dde_fund_flow_history` | 历史 DDE 资金流 | 主键 `(stock_code, trade_date)`；从 XLSX 批量导入，独立于实时三时段快照，保留资金、行情字段和来源文件 |
| `t_stock_dde_signal` | DDE 资金选股信号 | 主键 `(stock_code, trade_date, snapshot_slot, signal_side)`；流入、流出各 Top30，保存排名、快照参考买入价、市值、成交额、主力/总净流入和主力净流入占市值比 |
| `t_stock_55d_main_fund_flow` | 连续55日主力资金流向 | 主键 `(stock_code, flow_date)`；iWenCai 返回的逐日主力净流入，附带抓取时的股票名称、最新价、涨跌幅和抓取日期 |
| `t_stock_quote_60` | 60 分钟级别日内行情 | `stock_code`、`trade_time`、开高低收、成交量额、涨跌幅；与 `t_stock_quote` 的实时快照区分 |
| `t_stock_capital` | 股本变动历史 | `stock_code`、`change_date`、流通/限售/总股本、变动比例、`reason` |
| `t_stock_formula` | 选股公式配置 | `id`、`name`、`code` |

## 选股结果与统计

| 表 | 作用 | 主键/关键字段 |
|---|---|---|
| `t_stock_xg_240_daily` | 日线选股原始结果及后续收益 | `trade_date`、`signal_name`、`stock_code`、`price`、`v_0_percent` 至 `v_5_percent`、`is_ok`、`nm` |
| `t_stock_xg_60_daily` | 60 分钟选股原始结果及后续收益 | 同日线结果；关键字段为 `trade_date`、`signal_name`、`stock_code`、收益列 |
| `t_stock_xg_240_result` | 日线盘中最终结果 | `trade_date`、`signal_name`、`stock_code`、`price`、`nm`、`remark` |
| `t_stock_xg_60_result` | 60 分钟盘中最终结果 | `trade_date`、`signal_name`、`stock_code`、`v_1` 至 `v_4`、收益列、`is_ok` |
| `t_stock_xg_result_5min` | 5 分钟早盘实盘结果 | 唯一键 `(trade_date, signal_name, stock_code)`；冻结首次入场价，尾盘补收盘价、收益和播报时间 |
| `t_stock_strategy_signal` | 新开发策略信号事件 | 唯一键 `(signal_id, trade_time, signal_type)`；当前仅保存三周期均线的入场、初始止损、5/15/60 分钟结构破坏及均线证据 JSON；`notified_at` 防止入场飞书重复发送，不关联既有选股结果 |
| `t_stock_xg_night_result` | 夜盘合并选股结果 | `source_type`、`trade_date`、`stock_code`、240/60 信号、收益列、`nm` |
| `t_stock_xg_night_3d_stat` | 夜盘 3 交易日统计 | `source_period`、`signal_name`、`trade_date`、总数、达标/超额数与比例 |
| `t_stock_theme_monthly_pool` | 概念月度核心池 | 主键 `(month_key, concept_key, stock_code)`；复用 10 日 NM 相似度和趋势共振，记录概念内有效同伴数与核心标记 |
| `t_stock_pair_trend_resonance` | 股票对 10 日趋势共振 | 主键 `(stock_code, related_stock_code, trade_date)`；代码按字典序存为无向对，尾盘/盘中一致性与共同正向比例 |
| `t_stock_daily_nm` | 盘后日线 NM 指标 | 主键 `(stock_code, trade_date)`；调用 stock-admin 日线 NM 评估接口保存，供趋势展示与股票对计算复用 |
| `t_stock_pair_nm_similarity` | 股票对 10 日 NM 趋势相似度 | 主键 `(stock_code, related_stock_code, trade_date)`；仅计算趋势共振表已有无向股票对，`nm_trend_similarity_pct` 为 NM 曲线相关度映射后的 `0~100` 分值 |

## 公司与 F10 信息

| 表 | 作用 | 主键/关键字段 |
|---|---|---|
| `t_stock_company_base_info` | 公司 F10 基本资料 | `stock_code`、公司名称、地址、网站、行业、上市日期、主营业务、经营范围 |
| `t_stock_stock_base_info` | 股票基础标识资料 | `stock_code`、`stock_name`、`full_name`、`stock_type`、`list_time`、`market_id` |
| `t_stock_a_manager_introduce` | 管理层介绍快照 | `stock_code`、`data_json`、`updated_at` |
| `t_stock_share_info` | 上市状态与市场标识 | `stock_code`、上市状态、市场/板块标识、`updated_at` |
| `t_stock_a_companies_list` | 同业公司明细 | `stock_code`、同业股票标识、名称、行业和行情字段 |
| `t_stock_a_stock_foucs` | A 股关注度排名 | 主键 `(stock_code, trade_date)`；全市场/行业排名及总数 |
| `t_stock_theme_key_points` | 主题要点 | `market_code`、`stock_code`、`title`、`content`、`update_date` |
| `t_stock_news` | 股票新闻 | 主键 `(stock_code, seq)`；标题、来源、作者、新闻时间、链接 |
| `t_stock_pub` | 股票公告 | 主键 `(stock_code, seq)`；`guid`、标题、发布日期、公告链接、类型 |
| `t_stock_product_price` | 产品价格序列 | 主键 `(stock_code, trade_date)`；`price`、`price_change_ratio` |
| `t_stock_related_product` | 关联产品与行情 | `stock_code`、关联股票标识、产品/行情关键字段、`updated_at` |
| `t_stock_holding_company` | 控股公司报告期明细 | `stock_code`、`report_date`、公司名称、持股/资产等字段 |
| `t_stock_fields_completion` | 事务所、网站及关联证券补充信息 | `stock_code`、事务所、网址、关联上市证券、`updated_at` |
| `t_stock_issuance_detail` | 发行详情和股本沿革 | `stock_code`、发行/变动日期、发行方式、股份及金额字段 |
| `t_stock_main_business_introduction` | 主营业务介绍键值明细 | `stock_code`、业务键、业务值、`updated_at` |
| `t_stock_main_business_structure` | 主营构成全量快照 | `stock_code`、`data_json`、`updated_at` |
| `t_stock_operate_business_data` | 经营业务指标时间序列 | `stock_code`、`tab_name`、`business_name`、`report_date`、`business_value` |
| `t_stock_business_review` | 业务回顾文本 | 主键 `(stock_code, report_date)`；董事会经营评述文本 |
| `t_stock_supplier_data` | 主要供应商明细 | `stock_code`、报告期、供应商名称、采购金额/占比等接口原始字段 |
| `t_stock_customer_data` | 主要客户明细 | `stock_code`、报告期、客户名称、销售金额/占比等接口原始字段 |
| `t_stock_controller_relation` | 控制人关系快照 | `controller_id`、`controller_name`、三类关系 JSON、`updated_at` |

## 概念与上涨区间

| 表 | 作用 | 主键/关键字段 |
|---|---|---|
| `t_stock_concept_list` | 股票所属概念列表 | 主键 `(stock_code, concept_id)`；概念名称/市场/指数代码、ETF、权重、标签和子概念 JSON |
| `t_stock_concept_components` | 概念成分股 | 主键 `(concept_market_id, quote_code, component_stock_code)`；概念标识、成分股、排名、龙头标识、动态指标 JSON |
| `t_stock_share_upward_cycle` | 股票上涨区间及原因 | 主键 `(stock_code, strategy, start_date, end_date)`；涨幅、交易日、资金、换手率、关联概念 JSON、原因文本 |

## 机构持仓

| 表 | 作用 | 主键/关键字段 |
|---|---|---|
| `t_stock_org_holder_rate` | 机构持仓比例汇总 | 主键 `(stock_code, date)`；机构数、持股数/市值/比例、变动及更新标识 |
| `t_stock_org_holder_tab` | 机构持仓分类汇总 | 主键 `(stock_code, report_date, tab_id)`；报告期、机构分类、持股比例和数量 |
| `t_stock_org_holder_detail` | 最新报告期机构持仓明细 | 主键 `(stock_code, report_date, org_id, trade_code)`；机构类型/名称、数量、市值、比例、变动、基金信息 |
| `t_stock_org_holder_rate_price` | 基金持仓比例和报告期价格 | 主键 `(stock_code, holder_category, report_date)`；`holder_rate`、`price`、更新标识 |
| `t_stock_org_holder_ipo` | 首发配售机构明细 | 主键 `(stock_code, ipo_date, org_name)`；机构类型、获配数量、申购数量、锁定期 |

## 财务、分红与融资

以下表已开发，并已使用 `000001` 完成一次手工样本抓取。

| 表 | 作用 | 主键/关键字段 |
|---|---|---|
| `t_stock_finance_announce_detail` | 财务报告公告明细 | 主键 `(stock_code, report_code)`；财年、审计意见、报告日期/期别、公告序号和链接 |
| `t_stock_financial_metrics` | 关键财务指标序列 | 主键 `(stock_code, metric_key, report_code, report_type)`；实际/预测/同比及区间字段、标签 JSON |
| `t_stock_financial_analysis` | 财报质量分析 | 主键 `(stock_code, report_code)`；营收、归母、扣非同比，增长分、质量差、标签和风险项 |
| `t_stock_financial_label` | 分红送转概率标签快照 | 主键 `(stock_code, label_key)`；标签名称、内容、说明、明细数组 JSON |
| `t_stock_financial_programme` | 分红方案明细 | 主键 `(stock_code, report_period)`；董事会/股东日期、方案、金额/比例、进度和对象 |
| `t_stock_financial_additional` | 融资增发快照 | 主键 `stock_code`；5 个增发统计字段、未知明细 JSON |
| `t_stock_financial_allotment` | 配股融资快照 | 主键 `stock_code`；5 个配股统计字段、未知明细 JSON |
| `t_stock_financial_dividend_ratio` | 分红能力比例快照 | 主键 `stock_code`；分红比例、累计现金分红、归母净利润均值、起始日期 |

## JSON 字段说明

| 表.字段 | JSON 类型 | 内容与使用方式 |
|---|---|---|
| `t_stock_a_manager_introduce.data_json` | 数组/对象 | 接口完整管理层数据；按 `json.loads` 后读取，不依赖固定成员字段。 |
| `t_stock_main_business_structure.data_json` | 数组 | 多报告期、行业/产品/地区主营构成及金额、比例、毛利率。 |
| `t_stock_concept_list.tags_json` | 数组 | 概念标签列表。 |
| `t_stock_concept_list.sub_concepts_json` | 数组 | 子概念、关联股票和说明；不再拆分子表。 |
| `t_stock_concept_components.indexes_json` | 对象 | 成分股的动态行情/财务指标，键随接口变化。 |
| `t_stock_share_upward_cycle.related_concepts_json` | 数组 | 上涨区间关联概念名称。 |
| `t_stock_controller_relation.holder_controller_json` | 数组 | 控股股东控制关系明细。 |
| `t_stock_controller_relation.final_controller_json` | 数组 | 最终控制人关系明细。 |
| `t_stock_controller_relation.actual_controller_json` | 数组 | 实际控制人关系明细。 |
| `t_stock_financial_metrics.label_info_json` | 对象或数组 | 指标标签、单位等扩展信息，可为空。 |
| `t_stock_financial_label.string_array_detail_json` | 数组 | 分红/送转概率判断依据文本，含数值与单位占位格式。 |
| `t_stock_financial_additional.additional_details_json` | 数组 | 融资增发明细；当前接口样例为空，保留原始结构等待字段稳定。 |
| `t_stock_financial_allotment.allotment_details_json` | 数组 | 配股融资明细；当前接口样例为空，保留原始结构等待字段稳定。 |

## 查询约定

```sql
-- JSON 数组是否包含值（SQLite JSON1 可用时）
SELECT stock_code
FROM t_stock_share_upward_cycle, json_each(related_concepts_json)
WHERE json_each.value = '锂电池概念';

-- 当前快照表直接按股票读取
SELECT *
FROM t_stock_financial_label
WHERE stock_code = '001203';
```

使用 JSON 字段前应确认 SQLite 环境启用 JSON1；未启用时在应用层 `json.loads` 后处理，避免用字符串 `LIKE` 替代结构化查询。

<!-- GENERATED SQLITE DDL: BEGIN -->

## 自动导出的 SQLite 建表语句

- 服务器数据库：`/root/data/stock_stat.db`
- Windows 默认数据库：`stock_cron/data/stock_stat.db`（由 `STOCK_STAT_DB_PATH` 覆盖）
- 导出时间：`2026-08-08T17:08:46`
- 内容只含结构；除非显式使用 `--sample-row`，不导出任何数据。

### 表

#### `t_bond_quote`

```sql
CREATE TABLE "t_bond_quote" (stock_code TEXT NOT NULL, market_date TEXT NOT NULL, "current_amount" TEXT, "last_px" TEXT, "vol_ratio" TEXT, "dyn_pb_rate" TEXT, "amplitude" TEXT, "min5_chgpct" TEXT, "wavg_px" TEXT, "prod_name" TEXT, "shares_per_hand" TEXT, "debt_fund_value" TEXT, "market_value" TEXT, "bps" TEXT, "turnover_ratio" TEXT, "entrust_rate" TEXT, "entrust_diff" TEXT, "circulation_amount" TEXT, "circulation_value" TEXT, "eps" TEXT, "preclose_px" TEXT, "updown_days" TEXT, "px_change_rate_5days" TEXT, "px_change_rate_10days" TEXT, "px_change_rate_20days" TEXT, "px_change_rate_60days" TEXT, "min1_chgpct" TEXT, "min3_chgpct" TEXT, "turnover_1mins" TEXT, "turnover_3mins" TEXT, "turnover_5mins" TEXT, "mrq_pb_rate" TEXT, "net_price" TEXT, "high_px" TEXT, "low_px" TEXT, "business_amount" TEXT, "convexity" TEXT, "premium_rate" TEXT, "debt_to_equity_px" TEXT, "debt_to_equity_value" TEXT, "straight_bond_value" TEXT, "exercise_yield_ratio" TEXT, "mac_duration" TEXT, "effective_duration" TEXT, "yield_ratio_change" TEXT, "debt_to_equity_rate" TEXT, "straight_bond_premium_rate" TEXT, "business_balance" TEXT, "open_px" TEXT, "bid_grp" TEXT, "offer_grp" TEXT, "trade_status" TEXT, "data_timestamp" TEXT, "up_px" TEXT, "down_px" TEXT, "business_amount_in" TEXT, "business_amount_out" TEXT, "w52_low_px" TEXT, "w52_high_px" TEXT, "px_change" TEXT, "px_change_rate" TEXT, "trade_mins" TEXT, "total_shares" TEXT, "pe_rate" TEXT, "special_marker" TEXT, "total_offerqty" TEXT, "total_bidqty" TEXT, "addi_tradetime_bits" TEXT, "last_yield_ratio" TEXT, "open_yield_ratio" TEXT, "high_yield_ratio" TEXT, "low_yield_ratio" TEXT, "close_yield_ratio" TEXT, "wavg_yield_ratio" TEXT, "preclose_yield_ratio" TEXT, "prewavg_yield_ratio" TEXT, "fund_discount_value" TEXT, "last_dirty_px" TEXT, "open_dirty_px" TEXT, "high_dirty_px" TEXT, "low_dirty_px" TEXT, "bid1_exec_yield_ratio" TEXT, "offer1_exec_yield_ratio" TEXT, "cb_yield_ratio" TEXT, "cb_net_px" TEXT, "cb_dirty_px" TEXT, "preclose_dirty_px" TEXT, "cs_yield_ratio" TEXT, "cs_net_px" TEXT, "cs_dirty_px" TEXT, "avg_px_rate" TEXT, "preclose_avg_rate" TEXT, "avg_px_up_down_rate" TEXT, "prod_name_ext" TEXT, "auction_px" TEXT, "auction_vol" TEXT, "auction_val" TEXT, "interest_rate" TEXT, "bond_trade_type" TEXT, "year_pxchange_rate" TEXT, PRIMARY KEY (stock_code, market_date));
```

#### `t_fund_quote`

```sql
CREATE TABLE "t_fund_quote" (stock_code TEXT NOT NULL, market_date TEXT NOT NULL, "iopv" TEXT, "current_amount" TEXT, "last_px" TEXT, "vol_ratio" TEXT, "dyn_pb_rate" TEXT, "amplitude" TEXT, "min5_chgpct" TEXT, "wavg_px" TEXT, "prod_name" TEXT, "shares_per_hand" TEXT, "debt_fund_value" TEXT, "market_value" TEXT, "bps" TEXT, "amount" TEXT, "turnover_ratio" TEXT, "entrust_rate" TEXT, "entrust_diff" TEXT, "circulation_amount" TEXT, "circulation_value" TEXT, "eps" TEXT, "prev_amount" TEXT, "preclose_px" TEXT, "updown_days" TEXT, "px_change_rate_5days" TEXT, "px_change_rate_10days" TEXT, "px_change_rate_20days" TEXT, "px_change_rate_60days" TEXT, "min1_chgpct" TEXT, "min3_chgpct" TEXT, "turnover_1mins" TEXT, "turnover_3mins" TEXT, "turnover_5mins" TEXT, "mrq_pb_rate" TEXT, "high_px" TEXT, "low_px" TEXT, "business_amount" TEXT, "premium_rate" TEXT, "iopv_scale" TEXT, "business_count" TEXT, "business_balance" TEXT, "open_px" TEXT, "bid_grp" TEXT, "offer_grp" TEXT, "trade_status" TEXT, "data_timestamp" TEXT, "up_px" TEXT, "down_px" TEXT, "business_amount_in" TEXT, "business_amount_out" TEXT, "w52_low_px" TEXT, "w52_high_px" TEXT, "px_change" TEXT, "px_change_rate" TEXT, "trade_mins" TEXT, "total_shares" TEXT, "pe_rate" TEXT, "special_marker" TEXT, "business_balance_scale" TEXT, "total_offerqty" TEXT, "total_bidqty" TEXT, "addi_tradetime_bits" TEXT, "fund_discount_value" TEXT, "open_flag" TEXT, "prod_name_ext" TEXT, "ttm_pe_rate" TEXT, "static_pe_rate" TEXT, "eps_ttm" TEXT, "eps_year" TEXT, "auction_px" TEXT, "auction_vol" TEXT, "auction_val" TEXT, "year_pxchange_rate" TEXT, PRIMARY KEY (stock_code, market_date));
```

#### `t_future_product`

```sql
CREATE TABLE t_future_product (market_code TEXT NOT NULL, product_code TEXT NOT NULL, market_name TEXT, product_name TEXT, type_unitname TEXT, px_scale TEXT, px_precision TEXT, wavg_px_precision TEXT, init_date TEXT, trade_sessions_json TEXT NOT NULL, PRIMARY KEY (market_code, product_code));
```

#### `t_future_quote`

```sql
CREATE TABLE t_future_quote (stock_code TEXT NOT NULL, market_date TEXT NOT NULL, quote_timestamp TEXT NOT NULL, market_code TEXT NOT NULL, product_code TEXT NOT NULL, "settlement" TEXT, "prev_settlement" TEXT, "current_amount" TEXT, "last_px" TEXT, "vol_ratio" TEXT, "amplitude" TEXT, "min5_chgpct" TEXT, "wavg_px" TEXT, "prod_name" TEXT, "shares_per_hand" TEXT, "market_value" TEXT, "amount" TEXT, "entrust_rate" TEXT, "entrust_diff" TEXT, "prev_amount" TEXT, "amount_delta" TEXT, "preclose_px" TEXT, "px_change_rate_5days" TEXT, "px_change_rate_10days" TEXT, "px_change_rate_20days" TEXT, "px_change_rate_60days" TEXT, "high_px" TEXT, "low_px" TEXT, "business_amount" TEXT, "business_balance" TEXT, "open_px" TEXT, "bid_grp" TEXT, "offer_grp" TEXT, "trade_status" TEXT, "data_timestamp" TEXT, "up_px" TEXT, "down_px" TEXT, "business_amount_in" TEXT, "business_amount_out" TEXT, "w52_low_px" TEXT, "w52_high_px" TEXT, "px_change" TEXT, "px_change_rate" TEXT, "trade_mins" TEXT, "contract_unit" TEXT, "record_time" TEXT, "open_vol" TEXT, "close_vol" TEXT, "change_main_flag" TEXT, "prod_name_ext" TEXT, "contract_classification" TEXT, "year_pxchange_rate" TEXT, PRIMARY KEY (stock_code, market_date, quote_timestamp));
```

#### `t_hk_stock_quote`

```sql
CREATE TABLE "t_hk_stock_quote" (stock_code TEXT NOT NULL, market_date TEXT NOT NULL, "current_amount" TEXT, "last_px" TEXT, "vol_ratio" TEXT, "dyn_pb_rate" TEXT, "amplitude" TEXT, "min5_chgpct" TEXT, "wavg_px" TEXT, "prod_name" TEXT, "shares_per_hand" TEXT, "market_value" TEXT, "bps" TEXT, "amount" TEXT, "turnover_ratio" TEXT, "entrust_rate" TEXT, "entrust_diff" TEXT, "circulation_amount" TEXT, "circulation_value" TEXT, "eps" TEXT, "prev_amount" TEXT, "preclose_px" TEXT, "updown_days" TEXT, "px_change_rate_5days" TEXT, "px_change_rate_10days" TEXT, "px_change_rate_20days" TEXT, "px_change_rate_60days" TEXT, "min1_chgpct" TEXT, "min3_chgpct" TEXT, "turnover_1mins" TEXT, "turnover_3mins" TEXT, "turnover_5mins" TEXT, "mrq_pb_rate" TEXT, "high_px" TEXT, "low_px" TEXT, "business_amount" TEXT, "business_balance" TEXT, "open_px" TEXT, "bid_grp" TEXT, "offer_grp" TEXT, "trade_status" TEXT, "data_timestamp" TEXT, "business_amount_in" TEXT, "business_amount_out" TEXT, "w52_low_px" TEXT, "w52_high_px" TEXT, "px_change" TEXT, "px_change_rate" TEXT, "trade_mins" TEXT, "total_shares" TEXT, "pe_rate" TEXT, "special_marker" TEXT, "exercise_date" TEXT, "exercise_price" TEXT, "issue_date" TEXT, "last_ext_px" TEXT, "ttm_pe_rate" TEXT, "static_pe_rate" TEXT, "eps_ttm" TEXT, "eps_year" TEXT, "year_pxchange_rate" TEXT, PRIMARY KEY (stock_code, market_date));
```

#### `t_stock_55d_fund_concept_daily`

```sql
CREATE TABLE t_stock_55d_fund_concept_daily (
            signal_date TEXT NOT NULL,
            strategy TEXT NOT NULL,
            concept_id TEXT NOT NULL,
            concept_name TEXT NOT NULL,
            stock_count INTEGER NOT NULL,
            inflow_stock_count INTEGER NOT NULL,
            flow_10d REAL NOT NULL,
            flow_55d REAL NOT NULL,
            market_cap REAL NOT NULL,
            strength_55d REAL,
            rank_no INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (signal_date, strategy, concept_id)
        );
```

#### `t_stock_55d_fund_signal`

```sql
CREATE TABLE t_stock_55d_fund_signal (
            stock_code TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            strategy TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            industry TEXT NOT NULL DEFAULT '',
            entry_close REAL NOT NULL,
            market_cap REAL,
            flow_5d REAL NOT NULL,
            flow_10d REAL NOT NULL,
            flow_20d REAL NOT NULL,
            flow_55d REAL NOT NULL,
            inflow_days_55d INTEGER NOT NULL,
            consecutive_inflow_days INTEGER NOT NULL,
            max_single_flow_ratio REAL,
            strength_10d REAL,
            strength_55d REAL,
            flow_acceleration REAL,
            price_return_20d REAL,
            concept_inflow_ratio REAL,
            signal_score REAL NOT NULL,
            return_1d REAL,
            return_3d REAL,
            return_5d REAL,
            return_10d REAL,
            return_20d REAL,
            max_return_20d REAL,
            max_drawdown_20d REAL,
            evaluated_days INTEGER NOT NULL DEFAULT 0,
            evaluated_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, signal_date, strategy, signal_type)
        );
```

#### `t_stock_55d_main_fund_flow`

```sql
CREATE TABLE t_stock_55d_main_fund_flow (stock_code TEXT NOT NULL, flow_date TEXT NOT NULL, stock_name TEXT NOT NULL DEFAULT '', main_net_amount REAL, latest_price REAL, change_pct REAL, captured_date TEXT NOT NULL, captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (stock_code, flow_date));
```

#### `t_stock_a_companies_list`

```sql
CREATE TABLE t_stock_a_companies_list (
            stock_code TEXT NOT NULL,
            field TEXT NOT NULL,
            company_code TEXT NOT NULL,
            company_name TEXT NOT NULL,
            company_url TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (stock_code, company_code)
        );
```

#### `t_stock_a_manager_introduce`

```sql
CREATE TABLE t_stock_a_manager_introduce (
            stock_code TEXT PRIMARY KEY,
            data_json TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_a_stock_foucs`

```sql
CREATE TABLE t_stock_a_stock_foucs (
            stock_code TEXT NOT NULL,
            trade_date INTEGER NOT NULL,
            all_rank INTEGER,
            all_num INTEGER,
            industry_rank INTEGER,
            industry_num INTEGER,
            PRIMARY KEY (stock_code, trade_date)
        );
```

#### `t_stock_business_review`

```sql
CREATE TABLE t_stock_business_review (
            stock_code TEXT NOT NULL,
            report_date TEXT NOT NULL,
            directorate_business_comment TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, report_date)
        );
```

#### `t_stock_capital`

```sql
CREATE TABLE t_stock_capital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            change_date TEXT NOT NULL,
            circulated_shares TEXT,
            non_circulated_shares TEXT,
            limited_shares TEXT,
            total_shares TEXT,
            change_percent TEXT,
            reason TEXT,
            circulated_shares_val INTEGER,
            non_circulated_shares_val INTEGER,
            limited_shares_val INTEGER,
            total_shares_val INTEGER,
            change_percent_val REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_company_base_info`

```sql
CREATE TABLE t_stock_company_base_info (
            org_name TEXT,
            code_name TEXT PRIMARY KEY,
            address TEXT,
            phone TEXT,
            website TEXT,
            post_code TEXT,
            logo TEXT,
            ths_url TEXT,
            image TEXT,
            video TEXT,
            tags TEXT,
            describe TEXT,
            industry TEXT,
            xsb_industry TEXT,
            area TEXT,
            management TEXT,
            staff TEXT,
            list_date TEXT,
            list_address TEXT,
            market_id TEXT,
            issue_price TEXT,
            bonus TEXT,
            financing TEXT,
            profitable_business TEXT,
            main_business TEXT,
            base_business TEXT,
            business_scope TEXT,
            business_nature TEXT,
            product TEXT,
            intro TEXT,
            used_name TEXT
        , stock_code TEXT);
```

#### `t_stock_concept_components`

```sql
CREATE TABLE t_stock_concept_components (
            concept_id INTEGER,
            concept_name TEXT,
            concept_market_id TEXT NOT NULL,
            quote_code TEXT NOT NULL,
            component_stock_code TEXT NOT NULL,
            component_market_id TEXT,
            component_stock_name TEXT,
            component_rank INTEGER,
            is_leading INTEGER,
            explain TEXT,
            indexes_json TEXT NOT NULL DEFAULT '{}',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (concept_market_id, quote_code, component_stock_code)
        );
```

#### `t_stock_concept_list`

```sql
CREATE TABLE t_stock_concept_list (
            stock_code TEXT NOT NULL,
            concept_id INTEGER NOT NULL,
            concept_name TEXT,
            concept_market_id TEXT,
            quote_code TEXT,
            etf_market TEXT,
            etf_code TEXT,
            weight INTEGER,
            has_etf INTEGER,
            tags_json TEXT NOT NULL DEFAULT '[]',
            sub_concepts_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, concept_id)
        );
```

#### `t_stock_customer_data`

```sql
CREATE TABLE t_stock_customer_data (
            stock_code TEXT NOT NULL,
            report_date TEXT NOT NULL,
            company_name TEXT NOT NULL,
            sales_amount_ratio TEXT,
            sales_amount TEXT,
            item_type TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, report_date, company_name)
        );
```

#### `t_stock_daily_15`

```sql
CREATE TABLE t_stock_daily_15 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_time INTEGER NOT NULL,
            trade_date INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL,
            vol_rate REAL,
            percent REAL,
            changes REAL,
            pre_close REAL,
            remark TEXT NOT NULL DEFAULT ''
        );
```

#### `t_stock_daily_240`

```sql
CREATE TABLE t_stock_daily_240 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_date INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL,
            vol_rate REAL,
            percent REAL,
            changes REAL,
            pre_close REAL,
            remark TEXT NOT NULL DEFAULT ''
        );
```

#### `t_stock_daily_30min_history`

```sql
CREATE TABLE t_stock_daily_30min_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_time INTEGER NOT NULL,
            trade_date INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL,
            vol_rate REAL,
            percent REAL,
            changes REAL,
            pre_close REAL,
            remark TEXT NOT NULL DEFAULT ''
        );
```

#### `t_stock_daily_5`

```sql
CREATE TABLE t_stock_daily_5 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_time INTEGER NOT NULL,
            trade_date INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL,
            vol_rate REAL,
            percent REAL,
            changes REAL,
            pre_close REAL,
            remark TEXT NOT NULL DEFAULT ''
        );
```

#### `t_stock_daily_60`

```sql
CREATE TABLE t_stock_daily_60 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_time INTEGER NOT NULL,
            trade_date INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL,
            vol_rate REAL,
            percent REAL,
            changes REAL,
            pre_close REAL,
            remark TEXT NOT NULL DEFAULT ''
        );
```

#### `t_stock_daily_nm`

```sql
CREATE TABLE t_stock_daily_nm (
            stock_code TEXT NOT NULL,
            trade_date INTEGER NOT NULL,
            nm REAL NOT NULL,
            PRIMARY KEY (stock_code, trade_date)
        );
```

#### `t_stock_dde_fund_flow`

```sql
CREATE TABLE t_stock_dde_fund_flow (stock_code TEXT NOT NULL, trade_date TEXT NOT NULL, snapshot_slot TEXT NOT NULL, super_large_net_amount TEXT, large_net_amount TEXT, medium_net_amount TEXT, small_net_amount TEXT, market_cap TEXT, turnover_amount TEXT, captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, change_pct TEXT, entry_price TEXT, PRIMARY KEY (stock_code, trade_date, snapshot_slot));
```

#### `t_stock_dde_signal`

```sql
CREATE TABLE t_stock_dde_signal (stock_code TEXT NOT NULL, trade_date TEXT NOT NULL, snapshot_slot TEXT NOT NULL, signal_side TEXT NOT NULL, rank_no INTEGER NOT NULL, stock_name TEXT NOT NULL DEFAULT '', entry_price REAL, market_cap REAL NOT NULL DEFAULT 0, turnover_amount REAL NOT NULL DEFAULT 0, main_net_amount REAL NOT NULL, total_net_amount REAL NOT NULL, main_net_ratio REAL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (stock_code, trade_date, snapshot_slot, signal_side));
```

#### `t_stock_dde_signal_legacy`

```sql
CREATE TABLE "t_stock_dde_signal_legacy" (stock_code TEXT NOT NULL, trade_date TEXT NOT NULL, snapshot_slot TEXT NOT NULL, rank_no INTEGER NOT NULL, stock_name TEXT NOT NULL DEFAULT '', market_cap REAL NOT NULL DEFAULT 0, turnover_amount REAL NOT NULL DEFAULT 0, main_net_amount REAL NOT NULL, total_net_amount REAL NOT NULL, main_net_ratio REAL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (stock_code, trade_date, snapshot_slot));
```

#### `t_stock_fields_completion`

```sql
CREATE TABLE t_stock_fields_completion (
            stock_code TEXT PRIMARY KEY,
            eng_org_name TEXT,
            legal_representative TEXT,
            eng_register_address TEXT,
            lawyer_firm TEXT,
            accounting_firm TEXT,
            register_address TEXT,
            company_logo TEXT,
            register_capital TEXT,
            general_manager TEXT,
            websites TEXT,
            fax TEXT,
            region TEXT,
            listing_info TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_finance_announce_detail`

```sql
CREATE TABLE t_stock_finance_announce_detail (
            stock_code TEXT NOT NULL,
            report_code TEXT NOT NULL,
            fiscal_year TEXT NOT NULL,
            audit_opinion TEXT,
            report_name TEXT,
            report_date TEXT,
            report_period TEXT,
            announcement_seq TEXT,
            mobile_url TEXT,
            client_url TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, report_code)
        );
```

#### `t_stock_financial_additional`

```sql
CREATE TABLE t_stock_financial_additional (
            stock_code TEXT PRIMARY KEY,
            issue_num TEXT,
            issue_fail_num TEXT,
            issue_success_num TEXT,
            issue_ongoing_num TEXT,
            issue_raise_money TEXT,
            additional_details_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_financial_allotment`

```sql
CREATE TABLE t_stock_financial_allotment (
            stock_code TEXT PRIMARY KEY,
            issue_num TEXT,
            issue_fail_num TEXT,
            issue_success_num TEXT,
            issue_ongoing_num TEXT,
            issue_raise_money TEXT,
            allotment_details_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_financial_analysis`

```sql
CREATE TABLE t_stock_financial_analysis (stock_code TEXT NOT NULL, report_code TEXT NOT NULL, stock_name TEXT NOT NULL DEFAULT '', revenue_yoy REAL, parent_profit_yoy REAL, deduct_profit_yoy REAL, profit_quality_gap REAL, growth_score REAL, analysis_label TEXT NOT NULL, risk_flags TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, parent_profit REAL, deduct_profit REAL, revenue REAL, PRIMARY KEY (stock_code, report_code));
```

#### `t_stock_financial_dividend_ratio`

```sql
CREATE TABLE t_stock_financial_dividend_ratio (
            stock_code TEXT PRIMARY KEY,
            divided_result TEXT,
            show INTEGER,
            accumulated_cash_dividend TEXT,
            parent_holder_net_profit_avg TEXT,
            start_date TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_financial_label`

```sql
CREATE TABLE t_stock_financial_label (
            stock_code TEXT NOT NULL,
            label_key TEXT NOT NULL,
            label_name TEXT,
            content TEXT,
            detail TEXT,
            string_array_detail_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, label_key)
        );
```

#### `t_stock_financial_metrics`

```sql
CREATE TABLE t_stock_financial_metrics (
            stock_code TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            report_code TEXT NOT NULL,
            report_type TEXT NOT NULL,
            actual TEXT,
            forecast TEXT,
            yoy TEXT,
            high_bound TEXT,
            low_bound TEXT,
            high_bound_yoy TEXT,
            low_bound_yoy TEXT,
            label_info_json TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, metric_key, report_code, report_type)
        );
```

#### `t_stock_financial_programme`

```sql
CREATE TABLE t_stock_financial_programme (
            stock_code TEXT NOT NULL,
            report_period TEXT NOT NULL,
            board_date TEXT,
            holder_date TEXT,
            plan_date TEXT,
            equity_registration_date TEXT,
            ex_dividend_date TEXT,
            dividend_plan TEXT,
            is_progress INTEGER,
            per_ten_pre_tax_dividend_ratio_rmb TEXT,
            stock_dividend_total TEXT,
            dividend_total TEXT,
            payment_rate TEXT,
            pretax_dividend_rate TEXT,
            progress_code TEXT,
            progress_name TEXT,
            dividend_target TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, report_period)
        );
```

#### `t_stock_formula`

```sql
CREATE TABLE "t_stock_formula" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT NOT NULL,
  "code" TEXT NOT NULL
);
```

#### `t_stock_holding_company`

```sql
CREATE TABLE t_stock_holding_company (
            stock_code TEXT NOT NULL,
            holding_company_id TEXT NOT NULL,
            report_date TEXT NOT NULL,
            company_name TEXT,
            declare_date TEXT,
            company_type TEXT,
            hold_rate TEXT,
            product TEXT,
            is_merge TEXT,
            invest_money TEXT,
            register_capital TEXT,
            company_net TEXT,
            detail_url TEXT,
            announcement_date TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, holding_company_id, report_date)
        );
```

#### `t_stock_index_quote`

```sql
CREATE TABLE "t_stock_index_quote" (stock_code TEXT NOT NULL, market_date TEXT NOT NULL, source_group TEXT NOT NULL, "last_px" TEXT, "vol_ratio" TEXT, "amplitude" TEXT, "min5_chgpct" TEXT, "wavg_px" TEXT, "prod_name" TEXT, "shares_per_hand" TEXT, "market_value" TEXT, "turnover_ratio" TEXT, "entrust_rate" TEXT, "entrust_diff" TEXT, "circulation_amount" TEXT, "circulation_value" TEXT, "rise_count" TEXT, "fall_count" TEXT, "member_count" TEXT, "preclose_px" TEXT, "px_change_rate_5days" TEXT, "px_change_rate_10days" TEXT, "px_change_rate_20days" TEXT, "px_change_rate_60days" TEXT, "high_px" TEXT, "low_px" TEXT, "business_amount" TEXT, "business_balance" TEXT, "open_px" TEXT, "trade_status" TEXT, "data_timestamp" TEXT, "business_amount_in" TEXT, "business_amount_out" TEXT, "w52_low_px" TEXT, "w52_high_px" TEXT, "px_change" TEXT, "px_change_rate" TEXT, "trade_mins" TEXT, "total_shares" TEXT, "total_offerqty" TEXT, "total_bidqty" TEXT, "total_offer_turnover" TEXT, "total_bid_turnover" TEXT, "flat_number" TEXT, "index_rise_trend" TEXT, "index_fall_trend" TEXT, "up_limit_count" TEXT, "touch_up_limit_count" TEXT, "st_up_limit_count" TEXT, "st_touch_up_limit_count" TEXT, "down_limit_count" TEXT, "touch_down_limit_count" TEXT, "st_down_limit_count" TEXT, "st_touch_down_limit_count" TEXT, "rise_rate" TEXT, "halt_count" TEXT, "prod_name_ext" TEXT, "year_pxchange_rate" TEXT, "amount" TEXT, "prev_amount" TEXT, "last_ext_px" TEXT, PRIMARY KEY (stock_code, market_date));
```

#### `t_stock_issuance_detail`

```sql
CREATE TABLE t_stock_issuance_detail (
            stock_code TEXT PRIMARY KEY,
            sponsor TEXT,
            issuance_price TEXT,
            first_day_open_price TEXT,
            estimated_raised TEXT,
            issuance_num TEXT,
            history TEXT,
            establish_date TEXT,
            winning_rate TEXT,
            lead_underwriter TEXT,
            listing_date TEXT,
            actual_raised TEXT,
            issuance_pe TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_main_business_introduction`

```sql
CREATE TABLE t_stock_main_business_introduction (
            stock_code TEXT NOT NULL,
            field_name TEXT NOT NULL,
            field_value TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, field_name)
        );
```

#### `t_stock_main_business_structure`

```sql
CREATE TABLE t_stock_main_business_structure (
            stock_code TEXT PRIMARY KEY,
            data_json TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_margin_daily_analysis`

```sql
CREATE TABLE t_stock_margin_daily_analysis (
            stock_code TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            entry_close REAL,
            market_cap REAL,
            turnover_amount REAL,
            margin_buy_amount REAL,
            margin_repay_amount REAL,
            margin_net_buy_amount REAL,
            margin_balance REAL,
            margin_balance_change_1d REAL,
            margin_balance_change_5d REAL,
            margin_balance_change_10d REAL,
            margin_balance_change_20d REAL,
            margin_buy_turnover_ratio REAL,
            margin_balance_market_cap_ratio REAL,
            margin_balance_change_5d_ratio REAL,
            short_sell_amount REAL,
            short_balance REAL,
            short_balance_change_1d REAL,
            short_balance_change_5d REAL,
            short_sell_turnover_ratio REAL,
            short_balance_change_5d_ratio REAL,
            leverage_pressure REAL,
            margin_inflow_streak INTEGER NOT NULL DEFAULT 0,
            price_return_20d REAL,
            next_1d_return_pct REAL,
            next_3d_return_pct REAL,
            next_5d_return_pct REAL,
            next_10d_return_pct REAL,
            next_20d_return_pct REAL,
            max_return_20d REAL,
            max_drawdown_20d REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, trade_date)
        );
```

#### `t_stock_margin_rank_performance`

```sql
CREATE TABLE t_stock_margin_rank_performance (
            margin_trade_date INTEGER NOT NULL,
            signal_generated_date INTEGER NOT NULL,
            side TEXT NOT NULL CHECK(side IN ('long', 'short')),
            rank_no INTEGER NOT NULL CHECK(rank_no BETWEEN 1 AND 30),
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            score REAL NOT NULL,
            participation_ratio REAL NOT NULL,
            balance_change_ratio REAL NOT NULL,
            entry_trade_date INTEGER,
            entry_price REAL,
            entry_day_high REAL,
            first_sell_trade_date INTEGER,
            sell_window_end_date INTEGER,
            sell_window_high REAL,
            sell_window_max_return_pct REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, entry_day_close REAL, first_sell_day_high REAL, sell_window_end_high REAL, reported_at REAL,
            PRIMARY KEY (margin_trade_date, side, rank_no),
            UNIQUE (margin_trade_date, side, stock_code)
        );
```

#### `t_stock_margin_trading`

```sql
CREATE TABLE t_stock_margin_trading (stock_code TEXT NOT NULL, trade_date TEXT NOT NULL, market_code TEXT, stock_name TEXT, latest_price TEXT, margin_buy_amount TEXT, margin_balance TEXT, short_sell_volume TEXT, short_balance TEXT, margin_short_balance TEXT, price_change TEXT, price_change_pct TEXT, margin_balance_growth TEXT, margin_buy_growth TEXT, margin_repay_amount TEXT, short_balance_volume TEXT, short_repay_volume TEXT, margin_short_balance_growth TEXT, PRIMARY KEY (stock_code, trade_date));
```

#### `t_stock_news`

```sql
CREATE TABLE t_stock_news (
            stock_code TEXT NOT NULL,
            seq TEXT NOT NULL,
            title TEXT NOT NULL,
            mobile_url TEXT NOT NULL DEFAULT '',
            pc_url TEXT NOT NULL DEFAULT '',
            client_url TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT '',
            author TEXT,
            news_time INTEGER,
            news_date TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (stock_code, seq)
        );
```

#### `t_stock_operate_business_data`

```sql
CREATE TABLE t_stock_operate_business_data (
            stock_code TEXT NOT NULL,
            tab_name TEXT NOT NULL,
            business_name TEXT NOT NULL,
            report_date TEXT NOT NULL,
            business_value REAL,
            recent_declare_date TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, tab_name, business_name, report_date)
        );
```

#### `t_stock_org_holder_detail`

```sql
CREATE TABLE t_stock_org_holder_detail (
            stock_code TEXT NOT NULL,
            report_date TEXT NOT NULL,
            org_id TEXT NOT NULL DEFAULT '',
            trade_code TEXT NOT NULL DEFAULT '',
            org_type_code TEXT,
            org_type_name TEXT,
            org_name TEXT,
            holder_num TEXT,
            holder_market_value TEXT,
            holder_rate TEXT,
            holder_change TEXT,
            is_new INTEGER,
            fund_rank TEXT,
            fund_net_rate TEXT,
            is_jump INTEGER,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, report_date, org_id, trade_code)
        );
```

#### `t_stock_org_holder_ipo`

```sql
CREATE TABLE t_stock_org_holder_ipo (
            stock_code TEXT NOT NULL,
            ipo_date TEXT NOT NULL,
            org_name TEXT NOT NULL,
            org_type TEXT,
            allocate_num TEXT,
            order_num TEXT,
            lock_period TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, ipo_date, org_name)
        );
```

#### `t_stock_org_holder_rate`

```sql
CREATE TABLE "t_stock_org_holder_rate" (
  "stock_code" TEXT NOT NULL,
  "date" TEXT NOT NULL,
  "org_num" TEXT,
  "total_holder" TEXT,
  "total_market_value" TEXT,
  "total_rate" TEXT,
  "total_holder_change" TEXT,
  "total_holder_change_rate" TEXT,
  "is_updating" INTEGER,
  PRIMARY KEY ("stock_code", "date")
);
```

#### `t_stock_org_holder_rate_price`

```sql
CREATE TABLE t_stock_org_holder_rate_price (
            stock_code TEXT NOT NULL,
            holder_category TEXT NOT NULL,
            report_period TEXT NOT NULL,
            report_date TEXT NOT NULL,
            holder_rate TEXT,
            price TEXT,
            is_updating INTEGER,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, holder_category, report_date)
        );
```

#### `t_stock_org_holder_tab`

```sql
CREATE TABLE t_stock_org_holder_tab (
            stock_code TEXT NOT NULL,
            report_period TEXT NOT NULL,
            report_date TEXT NOT NULL,
            tab_id TEXT NOT NULL,
            tab_name TEXT,
            holder_rate TEXT,
            holder_num TEXT,
            is_updating INTEGER,
            PRIMARY KEY (stock_code, report_date, tab_id)
        );
```

#### `t_stock_pair_nm_similarity`

```sql
CREATE TABLE t_stock_pair_nm_similarity (
            stock_code TEXT NOT NULL,
            related_stock_code TEXT NOT NULL,
            trade_date INTEGER NOT NULL,
            nm_trend_similarity_pct REAL NOT NULL,
            PRIMARY KEY (stock_code, related_stock_code, trade_date)
        );
```

#### `t_stock_pair_related_cache`

```sql
CREATE TABLE t_stock_pair_related_cache (
            stock_code TEXT PRIMARY KEY,
            intraday_trade_date INTEGER,
            intraday_related_stocks TEXT NOT NULL DEFAULT '',
            nm_trade_date INTEGER,
            nm_trend_related_stocks TEXT NOT NULL DEFAULT ''
        );
```

#### `t_stock_pair_trend_resonance`

```sql
CREATE TABLE t_stock_pair_trend_resonance (
            stock_code TEXT NOT NULL,
            related_stock_code TEXT NOT NULL,
            trade_date INTEGER NOT NULL,
            tail_same_pct REAL NOT NULL,
            tail_positive_pct REAL NOT NULL,
            intraday_same_pct REAL NOT NULL,
            intraday_positive_pct REAL NOT NULL,
            PRIMARY KEY (stock_code, related_stock_code, trade_date)
        );
```

#### `t_stock_pool`

```sql
CREATE TABLE t_stock_pool (
            code TEXT PRIMARY KEY,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            market_code TEXT NOT NULL DEFAULT '',
            full_industry TEXT NOT NULL DEFAULT '',
            full_concept TEXT NOT NULL DEFAULT '',
            concept_num INTEGER NOT NULL DEFAULT 0,
            industry_1 TEXT,
            industry_2 TEXT,
            industry_3 TEXT,
            stock_type TEXT NOT NULL DEFAULT 'stock',
            capital REAL NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_product_price`

```sql
CREATE TABLE t_stock_product_price (
            stock_code TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            price REAL,
            price_change_ratio REAL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, trade_date)
        );
```

#### `t_stock_pub`

```sql
CREATE TABLE t_stock_pub (
            stock_code TEXT NOT NULL,
            seq TEXT NOT NULL,
            guid TEXT,
            title TEXT NOT NULL DEFAULT '',
            publish_time INTEGER,
            publish_date TEXT,
            mobile_url TEXT,
            pc_url TEXT,
            raw_url TEXT,
            notice_type TEXT,
            PRIMARY KEY (stock_code, seq)
        );
```

#### `t_stock_quote`

```sql
CREATE TABLE t_stock_quote (
                stock_code TEXT PRIMARY KEY,
                addi_tradetime_bits REAL,
                amount REAL,
                amplitude REAL,
                auction_px REAL,
                auction_val REAL,
                auction_vol REAL,
                bid_grp TEXT,
                bps REAL,
                business_amount REAL,
                business_amount_am REAL,
                business_amount_in REAL,
                business_amount_out REAL,
                business_balance REAL,
                business_balance_am REAL,
                business_balance_scale REAL,
                business_count REAL,
                business_last_closedate TEXT,
                circulation_amount REAL,
                circulation_value REAL,
                close_px REAL,
                current_amount REAL,
                data_timestamp REAL,
                debt_fund_value REAL,
                down_px REAL,
                dyn_pb_rate REAL,
                entrust_diff REAL,
                entrust_rate REAL,
                eps REAL,
                eps_ttm REAL,
                eps_year REAL,
                fund_discount_value REAL,
                high_px REAL,
                iopv REAL,
                last_px REAL,
                low_px REAL,
                market_date TEXT,
                market_value REAL,
                min1_chgpct REAL,
                min3_chgpct REAL,
                min5_chgpct REAL,
                mrq_pb_rate REAL,
                offer_grp TEXT,
                open_flag REAL,
                open_px REAL,
                osov_rate REAL,
                pe_rate REAL,
                preclose_px REAL,
                premium_rate REAL,
                prev_amount REAL,
                prod_name TEXT,
                prod_name_ext TEXT,
                px_change REAL,
                px_change_rate REAL,
                px_change_rate_10days REAL,
                px_change_rate_20days REAL,
                px_change_rate_5days REAL,
                px_change_rate_60days REAL,
                shares_per_hand REAL,
                special_marker REAL,
                static_pe_rate REAL,
                total_bidqty REAL,
                total_offerqty REAL,
                total_shares REAL,
                trade_mins REAL,
                trade_status TEXT,
                ttm_pe_rate REAL,
                turnover_1mins REAL,
                turnover_3mins REAL,
                turnover_5mins REAL,
                turnover_ratio REAL,
                up_px REAL,
                updown_days REAL,
                vol_ratio REAL,
                w52_high_px REAL,
                w52_low_px REAL,
                wavg_px REAL,
                year_pxchange_rate REAL
            , "iopv_scale" REAL);
```

#### `t_stock_related_product`

```sql
CREATE TABLE t_stock_related_product (
            stock_code TEXT NOT NULL,
            related_stock_code TEXT NOT NULL,
            stock_name TEXT,
            newest_product_name TEXT,
            price_change_ratio_pct TEXT,
            total_market_value TEXT,
            turnover_ratio_pct TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, related_stock_code)
        );
```

#### `t_stock_share_info`

```sql
CREATE TABLE t_stock_share_info (
            stock_code TEXT PRIMARY KEY,
            stock_name TEXT NOT NULL DEFAULT '',
            ths_code TEXT NOT NULL DEFAULT '',
            listing_date TEXT,
            status_id TEXT,
            status_name TEXT,
            market_id TEXT,
            is_listed INTEGER,
            is_de_listed INTEGER,
            list_addr TEXT,
            stock_type TEXT,
            type_code TEXT,
            market_code TEXT,
            market_name TEXT,
            special_description TEXT
        );
```

#### `t_stock_share_upward_cycle`

```sql
CREATE TABLE t_stock_share_upward_cycle (
            stock_code TEXT NOT NULL,
            strategy INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            range_incr_ratio REAL,
            trade_day_num INTEGER,
            related_concepts_json TEXT NOT NULL DEFAULT '[]',
            range_main_capital_net_inflow REAL,
            range_turnover_ratio REAL,
            range_incr_sum REAL,
            range_reason TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, strategy, start_date, end_date)
        );
```

#### `t_stock_single_kline`

```sql
CREATE TABLE t_stock_single_kline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_date INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            vol REAL,
            amount REAL
        );
```

#### `t_stock_stock_base_info`

```sql
CREATE TABLE t_stock_stock_base_info (
            stock_code TEXT PRIMARY KEY,
            stock_name TEXT NOT NULL DEFAULT '',
            full_name TEXT NOT NULL DEFAULT '',
            stock_type TEXT NOT NULL DEFAULT '',
            list_time TEXT,
            market_id TEXT,
            ths_code TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
```

#### `t_stock_strategy_signal`

```sql
CREATE TABLE t_stock_strategy_signal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            trade_time INTEGER NOT NULL,
            trade_date INTEGER NOT NULL,
            side TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            price REAL NOT NULL,
            stop_price REAL,
            ma20_5 REAL,
            ma20_15 REAL,
            ma20_60 REAL,
            reason_json TEXT NOT NULL DEFAULT '{}',
            notified_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(signal_id, trade_time, signal_type)
        );
```

#### `t_stock_supplier_data`

```sql
CREATE TABLE t_stock_supplier_data (
            stock_code TEXT NOT NULL,
            report_date TEXT NOT NULL,
            company_name TEXT NOT NULL,
            procurement_amount_ratio TEXT,
            procurement_amount TEXT,
            item_type TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stock_code, report_date, company_name)
        );
```

#### `t_stock_theme_key_points`

```sql
CREATE TABLE t_stock_theme_key_points (
            market_code TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            update_date TEXT NOT NULL,
            PRIMARY KEY (market_code, stock_code, title, update_date)
        );
```

#### `t_stock_theme_monthly_pool`

```sql
CREATE TABLE t_stock_theme_monthly_pool (
            month_key INTEGER NOT NULL,
            concept_key TEXT NOT NULL,
            concept_name TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            source_types TEXT NOT NULL DEFAULT 'concept_component',
            peer_count INTEGER NOT NULL,
            nm_similarity_pct REAL NOT NULL,
            trend_same_pct REAL NOT NULL,
            trend_positive_pct REAL NOT NULL,
            is_core INTEGER NOT NULL,
            PRIMARY KEY (month_key, concept_key, stock_code)
        );
```

#### `t_stock_triple_ma_watchlist`

```sql
CREATE TABLE t_stock_triple_ma_watchlist (
            stage TEXT NOT NULL CHECK(stage IN ('15m', '5m')),
            stock_code TEXT NOT NULL,
            side TEXT NOT NULL CHECK(side IN ('long', 'short')),
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (stage, stock_code)
        );
```

#### `t_stock_xg_240_daily`

```sql
CREATE TABLE t_stock_xg_240_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_name TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_date INTEGER NOT NULL,
            price REAL,
            v_0_percent REAL,
            v_1_percent REAL,
            v_2_percent REAL,
            v_3_percent REAL,
            v_4_percent REAL,
            v_5_percent REAL,
            min_day INTEGER,
            is_ok INTEGER NOT NULL DEFAULT 0,
            org_num REAL,
            concept_name TEXT NOT NULL DEFAULT '',
            nm REAL,
            UNIQUE(signal_name, stock_code, trade_date)
        );
```

#### `t_stock_xg_240_result`

```sql
CREATE TABLE "t_stock_xg_240_result" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "trade_date" INTEGER NOT NULL,
  "signal_name" TEXT NOT NULL,
  "stock_code" TEXT NOT NULL,
  "stock_name" TEXT,
  "price" REAL,
  "remark" TEXT DEFAULT '',
  "nm" REAL
);
```

#### `t_stock_xg_60_daily`

```sql
CREATE TABLE t_stock_xg_60_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_name TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            trade_date INTEGER NOT NULL,
            price REAL,
            v_0_percent REAL,
            v_1_percent REAL,
            v_2_percent REAL,
            v_3_percent REAL,
            v_4_percent REAL,
            v_5_percent REAL,
            min_day INTEGER,
            is_ok INTEGER NOT NULL DEFAULT 0,
            org_num REAL,
            concept_name TEXT NOT NULL DEFAULT '',
            nm REAL,
            UNIQUE(signal_name, stock_code, trade_date)
        );
```

#### `t_stock_xg_60_result`

```sql
CREATE TABLE "t_stock_xg_60_result" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "signal_name" TEXT NOT NULL,
  "stock_code" TEXT NOT NULL,
  "trade_date" INTEGER NOT NULL,
  "price" REAL,
  "v_1" INTEGER NOT NULL DEFAULT 0,
  "v_2" INTEGER NOT NULL DEFAULT 0,
  "v_3" INTEGER NOT NULL DEFAULT 0,
  "v_4" INTEGER NOT NULL DEFAULT 0,
  "v_0_percent" REAL,
  "v_1_percent" REAL,
  "v_2_percent" REAL,
  "v_3_percent" REAL,
  "v_4_percent" REAL,
  "v_5_percent" REAL,
  "min_day" INTEGER,
  "is_ok" INTEGER NOT NULL DEFAULT 0
);
```

#### `t_stock_xg_night_3d_stat`

```sql
CREATE TABLE t_stock_xg_night_3d_stat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_period TEXT NOT NULL,
            signal_name TEXT NOT NULL,
            trade_date INTEGER NOT NULL,
            total_count INTEGER NOT NULL DEFAULT 0,
            ok_count INTEGER NOT NULL DEFAULT 0,
            ok_rate REAL,
            super_count INTEGER NOT NULL DEFAULT 0,
            super_rate REAL,
            target_percent REAL NOT NULL DEFAULT 1.8,
            super_percent REAL NOT NULL DEFAULT 3.6,
            window_days INTEGER NOT NULL DEFAULT 3,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_period, signal_name, trade_date)
        );
```

#### `t_stock_xg_night_result`

```sql
CREATE TABLE t_stock_xg_night_result (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type INTEGER NOT NULL,
            trade_date INTEGER NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL DEFAULT '',
            price REAL,
            signal_name TEXT NOT NULL DEFAULT '',
            signal_60_name TEXT NOT NULL DEFAULT '',
            signal_240_name TEXT NOT NULL DEFAULT '',
            v_0_percent REAL,
            v_1_percent REAL,
            v_2_percent REAL,
            v_3_percent REAL,
            v_4_percent REAL,
            v_5_percent REAL,
            min_day INTEGER,
            is_ok INTEGER NOT NULL DEFAULT 0,
            org_num REAL,
            concept_name TEXT NOT NULL DEFAULT '',
            nm REAL,
            nm_60 REAL,
            nm_240 REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_type, trade_date, stock_code, signal_name, signal_60_name, signal_240_name)
        );
```

### 索引

#### `idx_t_stock_55d_fund_concept_daily_date`

```sql
CREATE INDEX idx_t_stock_55d_fund_concept_daily_date
        ON t_stock_55d_fund_concept_daily(signal_date, strategy, rank_no);
```

#### `idx_t_stock_55d_fund_signal_date`

```sql
CREATE INDEX idx_t_stock_55d_fund_signal_date
        ON t_stock_55d_fund_signal(signal_date, strategy, signal_type, signal_score DESC);
```

#### `idx_t_stock_55d_main_fund_flow_flow_date`

```sql
CREATE INDEX idx_t_stock_55d_main_fund_flow_flow_date ON t_stock_55d_main_fund_flow(flow_date);
```

#### `idx_t_stock_capital_stock_code`

```sql
CREATE INDEX idx_t_stock_capital_stock_code
        ON t_stock_capital(stock_code);
```

#### `idx_t_stock_company_base_info_stock_code`

```sql
CREATE INDEX idx_t_stock_company_base_info_stock_code ON t_stock_company_base_info(stock_code);
```

#### `idx_t_stock_daily_15_trade_date`

```sql
CREATE INDEX idx_t_stock_daily_15_trade_date ON t_stock_daily_15(trade_date);
```

#### `idx_t_stock_daily_240_trade_date`

```sql
CREATE INDEX idx_t_stock_daily_240_trade_date
        ON t_stock_daily_240(trade_date);
```

#### `idx_t_stock_daily_30min_history_trade_date`

```sql
CREATE INDEX idx_t_stock_daily_30min_history_trade_date ON t_stock_daily_30min_history(trade_date);
```

#### `idx_t_stock_daily_5_trade_date`

```sql
CREATE INDEX idx_t_stock_daily_5_trade_date ON t_stock_daily_5(trade_date);
```

#### `idx_t_stock_daily_60_trade_date`

```sql
CREATE INDEX idx_t_stock_daily_60_trade_date
        ON t_stock_daily_60(trade_date);
```

#### `idx_t_stock_dde_signal_rank`

```sql
CREATE INDEX idx_t_stock_dde_signal_rank ON "t_stock_dde_signal_legacy"(trade_date, snapshot_slot, rank_no);
```

#### `idx_t_stock_formula_name`

```sql
CREATE UNIQUE INDEX "idx_t_stock_formula_name"
ON "t_stock_formula" (
  "name" ASC
);
```

#### `idx_t_stock_margin_daily_analysis_date`

```sql
CREATE INDEX idx_t_stock_margin_daily_analysis_date
        ON t_stock_margin_daily_analysis(trade_date, leverage_pressure DESC);
```

#### `idx_t_stock_margin_rank_performance_stock_code`

```sql
CREATE INDEX idx_t_stock_margin_rank_performance_stock_code ON t_stock_margin_rank_performance(stock_code);
```

#### `idx_t_stock_pool_industry_1`

```sql
CREATE INDEX idx_t_stock_pool_industry_1 ON t_stock_pool(industry_1);
```

#### `idx_t_stock_pool_stock_code`

```sql
CREATE INDEX idx_t_stock_pool_stock_code ON t_stock_pool(stock_code);
```

#### `idx_t_stock_pool_stock_type`

```sql
CREATE INDEX idx_t_stock_pool_stock_type ON t_stock_pool(stock_type);
```

#### `idx_t_stock_single_kline_trade_date`

```sql
CREATE INDEX idx_t_stock_single_kline_trade_date ON t_stock_single_kline(trade_date);
```

#### `idx_t_stock_strategy_signal_signal_id`

```sql
CREATE INDEX idx_t_stock_strategy_signal_signal_id ON t_stock_strategy_signal(signal_id);
```

#### `idx_t_stock_xg_240_daily_signal_date`

```sql
CREATE INDEX idx_t_stock_xg_240_daily_signal_date
        ON t_stock_xg_240_daily(signal_name, trade_date);
```

#### `idx_t_stock_xg_240_daily_trade_date`

```sql
CREATE INDEX idx_t_stock_xg_240_daily_trade_date
        ON t_stock_xg_240_daily(trade_date);
```

#### `idx_t_stock_xg_240_result_signal_stock`

```sql
CREATE INDEX "idx_t_stock_xg_240_result_signal_stock"
ON "t_stock_xg_240_result" (
  "signal_name" ASC,
  "stock_code" ASC
);
```

#### `idx_t_stock_xg_240_result_trade_date`

```sql
CREATE INDEX "idx_t_stock_xg_240_result_trade_date"
ON "t_stock_xg_240_result" (
  "trade_date" ASC
);
```

#### `idx_t_stock_xg_60_daily_signal_date`

```sql
CREATE INDEX idx_t_stock_xg_60_daily_signal_date
        ON t_stock_xg_60_daily(signal_name, trade_date);
```

#### `idx_t_stock_xg_60_daily_trade_date`

```sql
CREATE INDEX idx_t_stock_xg_60_daily_trade_date
        ON t_stock_xg_60_daily(trade_date);
```

#### `idx_t_stock_xg_60_result_stock_code`

```sql
CREATE INDEX "idx_t_stock_xg_60_result_stock_code"
ON "t_stock_xg_60_result" (
  "stock_code" ASC
);
```

#### `idx_t_stock_xg_60_result_trade_date`

```sql
CREATE INDEX "idx_t_stock_xg_60_result_trade_date"
ON "t_stock_xg_60_result" (
  "trade_date" ASC
);
```

#### `idx_t_stock_xg_night_3d_stat_period_signal`

```sql
CREATE INDEX idx_t_stock_xg_night_3d_stat_period_signal
        ON t_stock_xg_night_3d_stat(source_period, signal_name);
```

#### `idx_t_stock_xg_night_3d_stat_trade_date`

```sql
CREATE INDEX idx_t_stock_xg_night_3d_stat_trade_date
        ON t_stock_xg_night_3d_stat(trade_date);
```

#### `idx_t_stock_xg_night_result_source_date`

```sql
CREATE INDEX idx_t_stock_xg_night_result_source_date
        ON t_stock_xg_night_result(source_type, trade_date);
```

#### `idx_t_stock_xg_night_result_trade_date`

```sql
CREATE INDEX idx_t_stock_xg_night_result_trade_date
        ON t_stock_xg_night_result(trade_date);
```

#### `idx_theme_pool_concept`

```sql
CREATE INDEX idx_theme_pool_concept ON t_stock_theme_monthly_pool(month_key, concept_key, is_core);
```

#### `ux_t_stock_capital_stock_code_change_date`

```sql
CREATE UNIQUE INDEX ux_t_stock_capital_stock_code_change_date
        ON t_stock_capital(stock_code, change_date);
```

#### `ux_t_stock_daily_15_stock_code_trade_time`

```sql
CREATE UNIQUE INDEX ux_t_stock_daily_15_stock_code_trade_time ON t_stock_daily_15(stock_code, trade_time);
```

#### `ux_t_stock_daily_240_stock_code_trade_date`

```sql
CREATE UNIQUE INDEX ux_t_stock_daily_240_stock_code_trade_date
        ON t_stock_daily_240(stock_code, trade_date);
```

#### `ux_t_stock_daily_30min_history_stock_code_trade_date`

```sql
CREATE UNIQUE INDEX ux_t_stock_daily_30min_history_stock_code_trade_date ON t_stock_daily_30min_history(stock_code, trade_date);
```

#### `ux_t_stock_daily_5_stock_code_trade_time`

```sql
CREATE UNIQUE INDEX ux_t_stock_daily_5_stock_code_trade_time ON t_stock_daily_5(stock_code, trade_time);
```

#### `ux_t_stock_daily_60_stock_code_trade_time`

```sql
CREATE UNIQUE INDEX ux_t_stock_daily_60_stock_code_trade_time
        ON t_stock_daily_60(stock_code, trade_time);
```

#### `ux_t_stock_single_kline_stock_code_trade_date`

```sql
CREATE UNIQUE INDEX ux_t_stock_single_kline_stock_code_trade_date ON t_stock_single_kline(stock_code, trade_date);
```

#### `ux_t_stock_xg_60_result_signal_stock_date`

```sql
CREATE UNIQUE INDEX "ux_t_stock_xg_60_result_signal_stock_date"
ON "t_stock_xg_60_result" (
  "signal_name" ASC,
  "stock_code" ASC,
  "trade_date" ASC
);
```

<!-- GENERATED SQLITE DDL: END -->
