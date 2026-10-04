SET @option_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=0 AND path='option' AND menu_type='M' LIMIT 1);

INSERT INTO sys_menu(menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期权决策总览',@option_menu_id,0,'overview','future/option-future-linkage','','OptionOverview',1,0,'C','0','0','future:option:list','dashboard','admin',NOW(),'admin',NOW(),'期权链与期货联动研究总览'
WHERE @option_menu_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM sys_menu WHERE parent_id=@option_menu_id AND path='overview');

INSERT INTO sys_role_menu(role_id,menu_id)
SELECT 1,menu_id FROM sys_menu WHERE parent_id=@option_menu_id AND path='overview'
AND NOT EXISTS(SELECT 1 FROM sys_role_menu x WHERE x.role_id=1 AND x.menu_id=sys_menu.menu_id);
