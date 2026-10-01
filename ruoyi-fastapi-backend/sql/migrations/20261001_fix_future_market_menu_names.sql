UPDATE sys_menu SET menu_name = '期货' WHERE parent_id = 0 AND menu_type = 'M' AND path = 'future';
UPDATE sys_menu SET menu_name = '国际行情', remark = '国际行情' WHERE menu_type = 'C' AND component = 'future/market' AND path = 'overseas';
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE parent_id = 0 AND menu_type = 'M' AND path = 'future'
AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = sys_menu.menu_id);
