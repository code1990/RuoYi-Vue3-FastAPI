START TRANSACTION;

SET @future_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '期货行情' AND menu_type = 'M' LIMIT 1);
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '期货行情', 0, 8, 'future', NULL, '', 'Future', 1, 0, 'M', '0', '0', '', 'trend', 'admin', NOW(), 'admin', NOW(), '期货行情'
WHERE @future_menu_id IS NULL;
SET @future_menu_id := COALESCE(@future_menu_id, (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '期货行情' AND menu_type = 'M' LIMIT 1));

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT menu_name, @future_menu_id, order_num, path, 'future/market', query, route_name, 1, 0, 'C', '0', '0', 'future:quote:list', 'trend', 'admin', NOW(), 'admin', NOW(), menu_name
FROM (SELECT '国内行情' menu_name, 1 order_num, 'domestic' path, '' query, 'FutureDomestic' route_name UNION ALL SELECT '国外行情', 2, 'overseas', 'scope=overseas', 'FutureOverseas') menus
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu existing WHERE existing.parent_id = @future_menu_id AND existing.menu_name = menus.menu_name);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE parent_id = @future_menu_id AND menu_name IN ('国内行情', '国外行情')
AND NOT EXISTS (SELECT 1 FROM sys_role_menu role_menu WHERE role_menu.role_id = 1 AND role_menu.menu_id = sys_menu.menu_id);

COMMIT;
