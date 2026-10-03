SET @future_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=0 AND path='future' AND menu_type='M' LIMIT 1);
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货历史数据',@future_menu_id,4,'history','ParentView','', 'FutureHistory',1,0,'M','0','0','','trend-charts','admin',NOW(),'admin',NOW(),'期货合约、序列与日线数据'
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@future_menu_id AND path='history');
UPDATE sys_menu SET menu_name='期货历史数据',component='ParentView',menu_type='M',perms='',icon='trend-charts',update_by='admin',update_time=NOW() WHERE parent_id=@future_menu_id AND path='history';
SET @history_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=@future_menu_id AND path='history' LIMIT 1);
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货合约目录',@history_menu_id,1,'contracts','future/history-contracts','','FutureHistoryContracts',1,0,'C','0','0','future:history:list','list','admin',NOW(),'admin',NOW(),'t_future_contract'
WHERE @history_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@history_menu_id AND path='contracts');
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货序列定义',@history_menu_id,2,'series','future/history-series','','FutureHistorySeries',1,0,'C','0','0','future:history:list','guide','admin',NOW(),'admin',NOW(),'t_future_series'
WHERE @history_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@history_menu_id AND path='series');
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货历史日线',@history_menu_id,3,'daily','future/history-daily','','FutureHistoryDaily',1,0,'C','0','0','future:history:list','data-line','admin',NOW(),'admin',NOW(),'t_future_daily_bar'
WHERE @history_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@history_menu_id AND path='daily');
INSERT INTO sys_role_menu (role_id,menu_id)
SELECT 1,menu_id FROM sys_menu WHERE parent_id=@history_menu_id
AND NOT EXISTS (SELECT 1 FROM sys_role_menu role_menu WHERE role_menu.role_id=1 AND role_menu.menu_id=sys_menu.menu_id);
