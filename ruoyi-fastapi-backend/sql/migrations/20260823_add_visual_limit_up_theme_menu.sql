-- Add limit-up theme visualization below the existing Visualization menu.

START TRANSACTION;

SET @visual_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '可视化' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '涨停题材', @visual_menu_id, 2, 'ztall', 'visual/ztall', '{"title":"涨停题材"}', 'VisualZtall', 1, 0, 'C', '0', '0', 'stock:visual:ztall', 'chart', 'admin', NOW(), 'admin', NOW(), '交易日涨停题材前15'
WHERE @visual_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'VisualZtall' AND menu_type = 'C');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE parent_id = @visual_menu_id AND route_name = 'VisualZtall'
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
