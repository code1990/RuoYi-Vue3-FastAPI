START TRANSACTION;

SET @visual_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '可视化' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '信号三表分析', @visual_menu_id, 2, 'signal-analysis', 'visual/signalAnalysis', '{"title":"信号三表分析"}', 'VisualSignalAnalysis', 1, 0, 'C', '0', '0', 'stock:visual:signal-analysis', 'chart', 'admin', NOW(), 'admin', NOW(), '原始、NM过滤和候选汇总统计'
WHERE @visual_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE route_name = 'VisualSignalAnalysis' AND menu_type = 'C');

UPDATE sys_menu SET component = 'visual/signalAnalysis', path = 'signal-analysis', order_num = 2,
    update_by = 'admin', update_time = NOW()
WHERE route_name = 'VisualSignalAnalysis' AND menu_type = 'C';

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE route_name = 'VisualSignalAnalysis' AND menu_type = 'C'
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = sys_menu.menu_id);

COMMIT;
