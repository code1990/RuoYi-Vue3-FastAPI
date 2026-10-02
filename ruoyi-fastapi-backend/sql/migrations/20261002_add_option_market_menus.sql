INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '期权', 0, 7, 'option', 'Layout', '', 'Option', 1, 0, 'M', '0', '0', '', 'chart', 'admin', NOW(), 'admin', NOW(), '大盘期权观察'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=0 AND path='option');

SET @option_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=0 AND path='option' AND menu_type='M' LIMIT 1);
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '期权品种', @option_menu_id, 1, 'varieties', 'future/option-varieties', '', 'OptionVarieties', 1, 0, 'C', '0', '0', 'future:option:list', 'chart', 'admin', NOW(), 'admin', NOW(), '大盘期权品种'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@option_menu_id AND path='varieties');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '大盘期权合约', @option_menu_id, 2, 'contracts', 'future/option-contracts', '', 'OptionContracts', 1, 0, 'C', '0', '0', 'future:option:list', 'chart', 'admin', NOW(), 'admin', NOW(), '大盘期权合约目录'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@option_menu_id AND path='contracts');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '大盘期权行情', @option_menu_id, 3, 'market', 'future/option-market', '', 'OptionMarket', 1, 0, 'C', '0', '0', 'future:option:list', 'chart', 'admin', NOW(), 'admin', NOW(), '分时与日线研究'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@option_menu_id AND path='market');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '交易时间轴', @option_menu_id, 4, 'timeline', 'future/option-timeline', '', 'OptionTimeline', 1, 0, 'C', '0', '0', 'future:option:list', 'chart', 'admin', NOW(), 'admin', NOW(), '期权交易时间轴'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id=@option_menu_id AND path='timeline');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE parent_id=@option_menu_id
AND NOT EXISTS (SELECT 1 FROM sys_role_menu role_menu WHERE role_menu.role_id=1 AND role_menu.menu_id=sys_menu.menu_id);

UPDATE sys_menu SET icon='chart', update_by='admin', update_time=NOW()
WHERE parent_id=@option_menu_id;
