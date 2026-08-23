-- DDE high-strength observation menu. Safe to run repeatedly.

START TRANSACTION;

SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT 'DDE高强度', @quant_menu_id, 16, 'dde-high-strength', 'stock/ddeObservation', '{"dimension":"high_strength"}', 'DdeHighStrength', 1, 0, 'C', '0', '0', 'stock:dde:observation:list', 'money', 'admin', NOW(), 'admin', NOW(), '尾盘主力资金强度不低于12%的DDE信号观察'
WHERE @quant_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = 'DDE高强度' AND menu_type = 'C');

UPDATE sys_menu
SET order_num = 17, update_by = 'admin', update_time = NOW()
WHERE parent_id = @quant_menu_id AND menu_name = 'DDE日内连续' AND menu_type = 'C';

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE parent_id = @quant_menu_id AND menu_name = 'DDE高强度'
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
