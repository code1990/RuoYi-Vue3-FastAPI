-- KDJ chart menu under Quant Statistics. Safe to run repeatedly.

START TRANSACTION;

SET @stat_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化统计' AND menu_type = 'M' LIMIT 1);
SET @kdj_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = @stat_menu_id AND path = 'kdj' AND menu_type = 'C' LIMIT 1);
SET @kdj_order_num := (
    SELECT COALESCE(MAX(order_num), 0) + 1
    FROM sys_menu
    WHERE parent_id = @stat_menu_id AND menu_id <> COALESCE(@kdj_menu_id, 0)
);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT 'KDJ', @stat_menu_id, @kdj_order_num, 'kdj', 'stat/kdj', '{"title":"KDJ统计"}', 'StatKdj', 1, 0, 'C', '0', '0', 'stock:stat:kdj:list', 'chart', 'admin', NOW(), 'admin', NOW(), 'K线与9、90周期KDJ统计'
WHERE @stat_menu_id IS NOT NULL AND @kdj_menu_id IS NULL;

SET @kdj_menu_id := COALESCE(@kdj_menu_id, (SELECT menu_id FROM sys_menu WHERE parent_id = @stat_menu_id AND path = 'kdj' AND menu_type = 'C' LIMIT 1));

UPDATE sys_menu
SET menu_name = 'KDJ', order_num = @kdj_order_num, component = 'stat/kdj', query = '{"title":"KDJ统计"}', route_name = 'StatKdj',
    is_frame = 1, is_cache = 0, visible = '0', status = '0', perms = 'stock:stat:kdj:list', icon = 'chart',
    update_by = 'admin', update_time = NOW(), remark = 'K线与9、90周期KDJ统计'
WHERE menu_id = @kdj_menu_id;

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @kdj_menu_id
WHERE @kdj_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @kdj_menu_id);

COMMIT;
