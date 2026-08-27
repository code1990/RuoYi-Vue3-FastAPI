SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=0 AND menu_name='量化回测' AND menu_type='M' LIMIT 1);
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '股票池',@quant_menu_id,35,'stock-pools','stock/stockPool','','StockPool',1,0,'C','0','0','stock:pools:list','money','admin',NOW(),'admin',NOW(),'stock-admin公式选股结果与交集'
WHERE @quant_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@quant_menu_id AND menu_name='股票池');
UPDATE sys_menu SET order_num=35,component='stock/stockPool',path='stock-pools' WHERE parent_id=@quant_menu_id AND menu_name='股票池';
INSERT INTO sys_role_menu (role_id,menu_id) SELECT 1,menu_id FROM sys_menu WHERE parent_id=@quant_menu_id AND menu_name='股票池' AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id=1 AND menu_id=sys_menu.menu_id);
