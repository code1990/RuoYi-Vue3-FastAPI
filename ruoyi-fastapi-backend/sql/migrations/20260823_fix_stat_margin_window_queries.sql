START TRANSACTION;

SET @stat_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化统计' AND menu_type = 'M' LIMIT 1);
UPDATE sys_menu SET query = CASE menu_name
    WHEN '融资2天' THEN '{"title":"融资2天统计","windowDays":2}'
    WHEN '融资3天' THEN '{"title":"融资3天统计","windowDays":3}'
    WHEN '融资5天' THEN '{"title":"融资5天统计","windowDays":5}'
END, update_by = 'admin', update_time = NOW()
WHERE parent_id = @stat_menu_id AND menu_name IN ('融资2天', '融资3天', '融资5天');

COMMIT;
