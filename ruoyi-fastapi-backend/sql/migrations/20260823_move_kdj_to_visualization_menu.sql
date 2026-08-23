-- Move KDJ from Algorithm Center to Visualization.

START TRANSACTION;

SET @algorithm_kdj_menu_id := (
    SELECT menu_id FROM sys_menu
    WHERE route_name = 'AlgorithmKdj' AND menu_type = 'C'
    LIMIT 1
);

DELETE FROM sys_role_menu
WHERE menu_id = @algorithm_kdj_menu_id;

DELETE FROM sys_menu
WHERE menu_id = @algorithm_kdj_menu_id;

SET @visual_menu_id := (
    SELECT menu_id FROM sys_menu
    WHERE parent_id = 0 AND menu_name = '可视化' AND menu_type = 'M'
    LIMIT 1
);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '可视化', 0, 9, 'visual', 'Layout', '', 'Visual', 1, 0, 'M', '0', '0', '', 'guide', 'admin', NOW(), 'admin', NOW(), '行情可视化菜单'
WHERE @visual_menu_id IS NULL;

SET @visual_menu_id := COALESCE(@visual_menu_id, (
    SELECT menu_id FROM sys_menu
    WHERE parent_id = 0 AND menu_name = '可视化' AND menu_type = 'M'
    LIMIT 1
));

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT 'KDJ', @visual_menu_id, 1, 'kdj', 'visual/kdj', '{"title":"KDJ统计"}', 'VisualKdj', 1, 0, 'C', '0', '0', 'stock:visual:kdj', 'guide', 'admin', NOW(), 'admin', NOW(), 'KDJ可视化'
WHERE @visual_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'VisualKdj' AND menu_type = 'C');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE (menu_id = @visual_menu_id OR parent_id = @visual_menu_id)
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
