-- Quant statistics menu placeholders. Safe to run repeatedly.

START TRANSACTION;

SET @stat_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化统计' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '量化统计', 0, 7, 'stat', 'Layout', '', 'Stat', 1, 0, 'M', '0', '0', '', 'chart', 'admin', NOW(), 'admin', NOW(), '量化统计占位菜单'
WHERE @stat_menu_id IS NULL;

SET @stat_menu_id := COALESCE(@stat_menu_id, (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化统计' AND menu_type = 'M' LIMIT 1));

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT menu_name, @stat_menu_id, order_num, path,
       CASE path
           WHEN 'dde' THEN 'stat/ddeFund'
           WHEN 'dde-combo' THEN 'stat/ddeCombo'
           WHEN 'dde-top30' THEN 'stat/ddeTop30'
           WHEN 'dde-hot-rank' THEN 'stat/ddeHotRank'
           WHEN 'dde-high-price' THEN 'stat/ddeObservation'
           WHEN 'dde-large-cap' THEN 'stat/ddeObservation'
           WHEN 'dde-intraday-combo' THEN 'stat/ddeObservation'
           WHEN 'main-fund' THEN 'stat/mainFund'
           ELSE 'stat/marginTrading'
       END, query, route_name, 1, 0, 'C', '0', '0', perms, 'chart', 'admin', NOW(), 'admin', NOW(), '量化统计功能占位'
FROM (
    SELECT 'DDE资金' AS menu_name, 10 AS order_num, 'dde' AS path, '{"title":"DDE资金统计"}' AS query, 'StatDde' AS route_name, 'stock:stat:dde:list' AS perms
    UNION ALL SELECT '2日DDE', 11, 'dde-combo', '{"title":"2日DDE统计"}', 'StatDdeCombo', 'stock:stat:dde-combo:list'
    UNION ALL SELECT 'DDE资金30', 12, 'dde-top30', '{"title":"DDE资金30统计"}', 'StatDdeTop30', 'stock:stat:dde-top30:list'
    UNION ALL SELECT 'DDE热度榜', 13, 'dde-hot-rank', '{"title":"DDE热度统计"}', 'StatDdeHotRank', 'stock:stat:dde-hot-rank:list'
    UNION ALL SELECT 'DDE高价股', 14, 'dde-high-price', '{"title":"DDE高价股统计"}', 'StatDdeHighPrice', 'stock:stat:dde-high-price:list'
    UNION ALL SELECT 'DDE高市值', 15, 'dde-large-cap', '{"title":"DDE高市值统计"}', 'StatDdeLargeCap', 'stock:stat:dde-large-cap:list'
    UNION ALL SELECT 'DDE日内连续', 16, 'dde-intraday-combo', '{"title":"DDE日内连续统计"}', 'StatDdeIntradayCombo', 'stock:stat:dde-intraday-combo:list'
    UNION ALL SELECT '主连资金', 20, 'main-fund', '{"title":"主连资金统计"}', 'StatMainFund', 'stock:stat:main-fund:list'
    UNION ALL SELECT '融资融券', 30, 'margin-trading', '{"title":"融资融券统计"}', 'StatMarginTrading', 'stock:stat:margin-trading:list'
    UNION ALL SELECT '融资2天', 31, 'margin-2d', '{"title":"融资2天统计"}', 'StatMargin2d', 'stock:stat:margin-2d:list'
    UNION ALL SELECT '融资3天', 32, 'margin-3d', '{"title":"融资3天统计"}', 'StatMargin3d', 'stock:stat:margin-3d:list'
    UNION ALL SELECT '融资5天', 33, 'margin-5d', '{"title":"融资5天统计"}', 'StatMargin5d', 'stock:stat:margin-5d:list'
) AS menus
WHERE @stat_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id = @stat_menu_id AND sys_menu.menu_name = menus.menu_name AND menu_type = 'C');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE (menu_id = @stat_menu_id OR parent_id = @stat_menu_id)
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
