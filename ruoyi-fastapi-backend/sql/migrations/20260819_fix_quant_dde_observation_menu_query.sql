START TRANSACTION;

UPDATE sys_menu
SET query = CASE menu_name
    WHEN 'DDE高价股' THEN '{"dimension":"high_price"}'
    WHEN 'DDE高市值' THEN '{"dimension":"large_cap"}'
    WHEN 'DDE日内连续' THEN '{"dimension":"intraday_combo"}'
END,
update_by = 'admin',
update_time = NOW()
WHERE parent_id = (
    SELECT menu_id FROM (
        SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1
    ) AS quant_menu
)
AND menu_type = 'C'
AND menu_name IN ('DDE高价股', 'DDE高市值', 'DDE日内连续');

COMMIT;
