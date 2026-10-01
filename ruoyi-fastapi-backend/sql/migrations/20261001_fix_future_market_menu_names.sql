UPDATE sys_menu SET menu_name = '期货' WHERE parent_id = 0 AND menu_type = 'M' AND path = 'future';
UPDATE sys_menu SET menu_name = '国际行情', remark = '国际行情' WHERE menu_type = 'C' AND component = 'future/market' AND path = 'overseas';
