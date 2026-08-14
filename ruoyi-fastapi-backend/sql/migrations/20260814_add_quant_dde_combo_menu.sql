START TRANSACTION;

SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1);
SET @dde_combo_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = '2日DDE' AND menu_type = 'C' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '2日DDE', @quant_menu_id, 2, 'dde-combo', 'stock/ddeCombo', '', 'DdeCombo', 1, 0, 'C', '0', '0', 'stock:dde:combo:list', 'money', 'admin', NOW(), 'admin', NOW(), '昨日今日DDE捡漏候选'
WHERE @quant_menu_id IS NOT NULL AND @dde_combo_menu_id IS NULL;

SET @dde_combo_menu_id := COALESCE(@dde_combo_menu_id, (SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = '2日DDE' AND menu_type = 'C' LIMIT 1));
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @dde_combo_menu_id WHERE @dde_combo_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @dde_combo_menu_id);

COMMIT;
