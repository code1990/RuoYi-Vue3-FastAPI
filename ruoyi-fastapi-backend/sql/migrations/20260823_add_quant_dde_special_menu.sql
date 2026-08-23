-- DDE special backtest menu. Safe to run repeatedly.

START TRANSACTION;

SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT 'DDE专项回测', @quant_menu_id, 18, 'dde-special', 'stock/ddeSpecial', '', 'DdeSpecial', 1, 0, 'C', '0', '0', 'stock:dde:observation:list', 'money', 'admin', NOW(), 'admin', NOW(), '高股价、高市值、高强度DDE信号的假设参与回测'
WHERE @quant_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = 'DDE专项回测' AND menu_type = 'C');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE parent_id = @quant_menu_id AND menu_name = 'DDE专项回测'
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
