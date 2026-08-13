-- Local/remote RuoYi MySQL migration: Quant backtest child menus.
-- Safe to run repeatedly; assigns menus to the administrator role (role_id = 1).

START TRANSACTION;

SET @quant_menu_id := (
    SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1
);

INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
)
SELECT
    '主连资金', @quant_menu_id, 2, 'main-fund', 'stock/mainFund', '', 'StockMainFund',
    1, 0, 'C', '0', '0', 'stock:mainFund:list', 'money',
    'admin', NOW(), 'admin', NOW(), '主连资金流'
WHERE @quant_menu_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = '主连资金' AND menu_type = 'C'
  );

SET @main_fund_menu_id := (
    SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = '主连资金' AND menu_type = 'C' LIMIT 1
);

INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
)
SELECT
    '融资融券', @quant_menu_id, 3, 'margin-trading', 'stock/marginTrading', '', 'StockMarginTrading',
    1, 0, 'C', '0', '0', 'stock:marginTrading:list', 'money',
    'admin', NOW(), 'admin', NOW(), '融资融券'
WHERE @quant_menu_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = '融资融券' AND menu_type = 'C'
  );

SET @margin_trading_menu_id := (
    SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = '融资融券' AND menu_type = 'C' LIMIT 1
);

INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
)
SELECT menu_name, @quant_menu_id, order_num, path, component, query, route_name,
       1, 0, 'C', '0', '0', perms, 'money', 'admin', NOW(), 'admin', NOW(), remark
FROM (
    SELECT '融资2天' AS menu_name, 4 AS order_num, 'margin-2d' AS path, 'stock/marginTrading' AS component,
           'windowDays=2' AS query, 'StockMargin2d' AS route_name, 'stock:margin:combo:list' AS perms, '2天综合融资排名' AS remark
    UNION ALL SELECT '融资3天', 5, 'margin-3d', 'stock/marginTrading', 'windowDays=3', 'StockMargin3d', 'stock:margin:combo:list', '3天综合融资排名'
    UNION ALL SELECT '融资5天', 6, 'margin-5d', 'stock/marginTrading', 'windowDays=5', 'StockMargin5d', 'stock:margin:combo:list', '5天综合融资排名'
) AS combo_menus
WHERE @quant_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = combo_menus.menu_name);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE parent_id = @quant_menu_id AND menu_name IN ('融资2天', '融资3天', '融资5天')
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = sys_menu.menu_id);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @main_fund_menu_id
WHERE @main_fund_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @main_fund_menu_id);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @margin_trading_menu_id
WHERE @margin_trading_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @margin_trading_menu_id);

COMMIT;
