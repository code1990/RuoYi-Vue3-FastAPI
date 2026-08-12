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

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @main_fund_menu_id
WHERE @main_fund_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @main_fund_menu_id);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @margin_trading_menu_id
WHERE @margin_trading_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @margin_trading_menu_id);

COMMIT;
