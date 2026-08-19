START TRANSACTION;

SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1);
SET @dde_hot_rank_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = 'DDE热度榜' AND menu_type = 'C' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT 'DDE热度榜', @quant_menu_id, 13, 'dde-hot-rank', 'stock/ddeHotRank', '', 'DdeHotRank', 1, 0, 'C', '0', '0', 'stock:dde:hot:list', 'money', 'admin', NOW(), 'admin', NOW(), 'DDE流入信号累计出现次数排行'
WHERE @quant_menu_id IS NOT NULL AND @dde_hot_rank_menu_id IS NULL;

SET @dde_hot_rank_menu_id := COALESCE(@dde_hot_rank_menu_id, (SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = 'DDE热度榜' AND menu_type = 'C' LIMIT 1));
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @dde_hot_rank_menu_id WHERE @dde_hot_rank_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @dde_hot_rank_menu_id);

COMMIT;
