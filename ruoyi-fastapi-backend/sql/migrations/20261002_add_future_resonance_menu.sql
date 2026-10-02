SET @future_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND path = 'future' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '期货共振', @future_menu_id, 4, 'resonance', 'future/resonance', '', 'FutureResonance', 1, 0, 'C', '0', '0', 'future:quote:list', 'chart', 'admin', NOW(), 'admin', NOW(), '国内外期货共振'
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id = @future_menu_id AND path = 'resonance');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE parent_id = @future_menu_id AND path = 'resonance'
AND NOT EXISTS (SELECT 1 FROM sys_role_menu role_menu WHERE role_menu.role_id = 1 AND role_menu.menu_id = sys_menu.menu_id);
