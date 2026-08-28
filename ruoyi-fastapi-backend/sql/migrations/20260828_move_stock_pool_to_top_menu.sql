UPDATE sys_menu
SET parent_id=0, order_num=40, path='stock-pools', component='ParentView', route_name='StockPools', menu_type='M', update_time=NOW(), update_by='admin'
WHERE menu_name='股票池' AND menu_type='C';

INSERT INTO sys_role_menu (role_id,menu_id)
SELECT 1,menu_id FROM sys_menu
WHERE menu_name='股票池' AND menu_type='C'
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id=1 AND menu_id=sys_menu.menu_id);
