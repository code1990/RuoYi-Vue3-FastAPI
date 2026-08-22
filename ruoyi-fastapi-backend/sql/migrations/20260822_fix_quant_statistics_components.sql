-- Point existing quant-statistics menu placeholders at their matching page components.

START TRANSACTION;

SET @stat_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化统计' AND menu_type = 'M' LIMIT 1);

UPDATE sys_menu
SET component = CASE path
    WHEN 'dde' THEN 'stat/ddeFund'
    WHEN 'dde-combo' THEN 'stat/ddeCombo'
    WHEN 'dde-top30' THEN 'stat/ddeTop30'
    WHEN 'dde-hot-rank' THEN 'stat/ddeHotRank'
    WHEN 'dde-high-price' THEN 'stat/ddeObservation'
    WHEN 'dde-large-cap' THEN 'stat/ddeObservation'
    WHEN 'dde-intraday-combo' THEN 'stat/ddeObservation'
    WHEN 'main-fund' THEN 'stat/mainFund'
    ELSE 'stat/marginTrading'
END,
update_by = 'admin',
update_time = NOW()
WHERE parent_id = @stat_menu_id
  AND path IN ('dde', 'dde-combo', 'dde-top30', 'dde-hot-rank', 'dde-high-price', 'dde-large-cap', 'dde-intraday-combo', 'main-fund', 'margin-trading', 'margin-2d', 'margin-3d', 'margin-5d');

COMMIT;
