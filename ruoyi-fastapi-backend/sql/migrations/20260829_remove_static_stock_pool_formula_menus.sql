DELETE role_menu
FROM sys_role_menu AS role_menu
JOIN sys_menu AS menu ON menu.menu_id = role_menu.menu_id
WHERE menu.parent_id = (SELECT menu_id FROM (SELECT menu_id FROM sys_menu WHERE menu_name = '股票池' AND parent_id = 0 LIMIT 1) AS stock_pool)
  AND menu.path LIKE 'formula-%';

DELETE FROM sys_menu
WHERE parent_id = (SELECT menu_id FROM (SELECT menu_id FROM sys_menu WHERE menu_name = '股票池' AND parent_id = 0 LIMIT 1) AS stock_pool)
  AND path LIKE 'formula-%';
