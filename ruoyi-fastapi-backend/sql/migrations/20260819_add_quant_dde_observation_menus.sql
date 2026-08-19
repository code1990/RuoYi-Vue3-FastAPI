START TRANSACTION;

SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT menu_name, @quant_menu_id, order_num, path, 'stock/ddeObservation', query, route_name, 1, 0, 'C', '0', '0', 'stock:dde:observation:list', 'money', 'admin', NOW(), 'admin', NOW(), remark
FROM (
    SELECT 'DDE高价股' AS menu_name, 14 AS order_num, 'dde-high-price' AS path, '{"dimension":"high_price"}' AS query, 'DdeHighPrice' AS route_name, '尾盘价格不低于80元的DDE信号观察' AS remark
    UNION ALL SELECT 'DDE高市值', 15, 'dde-large-cap', '{"dimension":"large_cap"}', 'DdeLargeCap', '尾盘市值不低于800亿的DDE信号观察'
    UNION ALL SELECT 'DDE日内连续', 16, 'dde-intraday-combo', '{"dimension":"intraday_combo"}', 'DdeIntradayCombo', '早午尾至少两个时段出现DDE信号的观察'
) AS menus
WHERE @quant_menu_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sys_menu WHERE parent_id = @quant_menu_id AND sys_menu.menu_name = menus.menu_name AND menu_type = 'C'
);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE parent_id = @quant_menu_id AND menu_name IN ('DDE高价股', 'DDE高市值', 'DDE日内连续')
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
