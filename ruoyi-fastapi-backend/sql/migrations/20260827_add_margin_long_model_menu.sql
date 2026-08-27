SET @quant_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1);
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '融资做多强度',@quant_menu_id,7,'margin-long-model','stock/marginLongModel','', 'MarginLongModel',1,0,'C','0','0','stock:margin:longModel:list','money','admin',NOW(),'admin',NOW(),'融资融券做多强度持续监控'
WHERE @quant_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@quant_menu_id AND menu_name='融资做多强度');
INSERT INTO sys_role_menu (role_id,menu_id) SELECT 1,menu_id FROM sys_menu WHERE parent_id=@quant_menu_id AND menu_name='融资做多强度' AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id=1 AND menu_id=sys_menu.menu_id);
