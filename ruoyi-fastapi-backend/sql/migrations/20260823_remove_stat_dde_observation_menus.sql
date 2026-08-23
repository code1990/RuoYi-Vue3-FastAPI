-- Remove observation-only menus from quant statistics.

START TRANSACTION;

SET @stat_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化统计' AND menu_type = 'M' LIMIT 1);

DELETE role_menu FROM sys_role_menu AS role_menu
JOIN sys_menu AS menu ON menu.menu_id = role_menu.menu_id
WHERE menu.parent_id = @stat_menu_id AND menu.menu_name IN ('DDE高价股', 'DDE高市值');

DELETE FROM sys_menu
WHERE parent_id = @stat_menu_id AND menu_name IN ('DDE高价股', 'DDE高市值');

COMMIT;
