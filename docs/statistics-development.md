# 统计功能开发文档

## DDE 强度、时段与 5 日结果

### 页面

- 路由：`/stat/dde`
- 页面：`ruoyi-fastapi-frontend/src/views/stat/ddeFund.vue`
- 接口：`GET /stock/dde/statistics?targetReturnPct=1.8`

### 目的

按 DDE 信号时段和资金强度，观察完整 5 日样本中达到目标收益的数量。

默认目标为 5 日内最高收益不低于 `1.8%`。没有完整 5 日收益的信号不参与统计。

### 数据口径

数据来自 `t_stock_dde_signal_performance`：

- 时段：`morning`（早盘）、`noon`（午盘）、`close`（尾盘）。
- 强度：主力净流入占市值低于 `5%`、`5%` 至低于 `15%`、不低于 `15%`。
- 达标：`max_return_t5_pct >= targetReturnPct`。
- 未达标：`max_return_t5_pct < targetReturnPct`。
- 横轴：最近 30 个有统计结果的交易日。
- 纵轴：完整 5 日样本数。

### 图表结构

每个交易日展示三个并列的堆叠柱，分别对应早盘、午盘、尾盘：

1. 每个柱以时段作为独立堆叠组。
2. 每个堆叠组由三个资金强度区间组成。
3. 每个强度区间继续分为“达标”和“未达标”。
4. 深色表示达标，浅色表示未达标；绿色、橙色、红色依次表示低、中、高资金强度。

因此柱高表示该时段的完整样本总数，柱内颜色同时表达资金强度和收益是否达标。

### 后续修改原则

- 改变收益阈值时，同时更新页面提示语与接口参数默认值。
- 新增时段前，先在后端排序规则和前端 `periods` 中同步定义标签。
- 不把未完成 5 日观察期的样本填入“未达标”，以免压低真实成功率。
- 图表仅展示统计结果，不承担 DDE 原始排序或题材热度联动展示。

## 2日 DDE 列表统计

- 路由：`/stat/dde-combo`
- 接口：`GET /stock/dde/combo/statistics?targetReturnPct=1.8`
- 数据仅来自 `t_stock_dde_combo_signal`，不混入其他 DDE 信号表。

同一股票的昨日与今日 DDE 出现次数相加后分为 `2次`、`3次`、`4次+`。仅 `T+1` 至 `T+5` 完整的样本入图；五日内任一天最高收益达到目标收益即为达标。每个交易日展示三档次数的并列堆叠柱，深色为达标、浅色为未达标。

## DDE资金30列表统计

- 路由：`/stat/dde-top30`
- 接口：`GET /stock/dde/top30/statistics?targetReturnPct=1.8`
- 数据仅来自 `t_stock_dde_30_signal_performance`。

仅早盘、午盘、尾盘参与统计，盘后记录不入图。每个交易日按三时段展示并列堆叠柱；完整5日样本中任一天最高收益达到目标收益为达标。

## DDE热度榜统计

- 路由：`/stat/dde-hot-rank`
- 数据直接来自 `GET /stock/dde/hot-rank/list?pageNum=1&pageSize=30` 的当前热度榜列表。

仅展示当前统计区间内排名前30的股票。股票为纵轴，早盘、午盘、尾盘 DDE 出现次数为横向堆叠柱；柱总长度即累计出现次数。
