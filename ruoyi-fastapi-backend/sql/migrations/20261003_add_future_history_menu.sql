SET @future_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=0 AND path='future' AND menu_type='M' LIMIT 1);
SET @history_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=@future_menu_id AND path='history' LIMIT 1);
UPDATE sys_menu SET parent_id=@future_menu_id,path='history-contracts',update_by='admin',update_time=NOW()
WHERE parent_id=@history_menu_id AND path='contracts';
UPDATE sys_menu SET parent_id=@future_menu_id,path='history-series',update_by='admin',update_time=NOW()
WHERE parent_id=@history_menu_id AND path='series';
UPDATE sys_menu SET parent_id=@future_menu_id,path='history-daily',update_by='admin',update_time=NOW()
WHERE parent_id=@history_menu_id AND path='daily';
DELETE FROM sys_role_menu WHERE menu_id=@history_menu_id;
DELETE FROM sys_menu WHERE menu_id=@history_menu_id;

INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货合约目录',@future_menu_id,4,'history-contracts','future/history-contracts','','FutureHistoryContracts',1,0,'C','0','0','future:history:list','list','admin',NOW(),'admin',NOW(),'t_future_contract'
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@future_menu_id AND path='history-contracts');
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货序列定义',@future_menu_id,5,'history-series','future/history-series','','FutureHistorySeries',1,0,'C','0','0','future:history:list','guide','admin',NOW(),'admin',NOW(),'t_future_series'
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@future_menu_id AND path='history-series');
INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '期货历史日线',@future_menu_id,6,'history-daily','future/history-daily','','FutureHistoryDaily',1,0,'C','0','0','future:history:list','data-line','admin',NOW(),'admin',NOW(),'t_future_daily_bar'
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@future_menu_id AND path='history-daily');
INSERT INTO sys_role_menu (role_id,menu_id)
SELECT 1,menu_id FROM sys_menu WHERE parent_id=@future_menu_id AND path IN ('history-contracts','history-series','history-daily')
AND NOT EXISTS (SELECT 1 FROM sys_role_menu role_menu WHERE role_menu.role_id=1 AND role_menu.menu_id=sys_menu.menu_id);
