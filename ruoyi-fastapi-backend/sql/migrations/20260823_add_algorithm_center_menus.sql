-- Algorithm center placeholders mirroring quant statistics.

START TRANSACTION;

SET @algorithm_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '算法中心' AND menu_type = 'M' LIMIT 1);

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT '算法中心', 0, 8, 'algorithm', 'Layout', '', 'Algorithm', 1, 0, 'M', '0', '0', '', 'guide', 'admin', NOW(), 'admin', NOW(), '算法模块占位菜单'
WHERE @algorithm_menu_id IS NULL;

SET @algorithm_menu_id := COALESCE(@algorithm_menu_id, (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '算法中心' AND menu_type = 'M' LIMIT 1));

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
SELECT menu_name, @algorithm_menu_id, order_num, path, component, query, route_name, 1, 0, 'C', '0', '0', 'stock:algorithm:list', 'guide', 'admin', NOW(), 'admin', NOW(), '算法模块占位'
FROM (
    SELECT 'DDE资金' AS menu_name, 10 AS order_num, 'dde' AS path, 'algorithm/ddeFund' AS component, '{"title":"DDE资金算法"}' AS query, 'AlgorithmDde' AS route_name
    UNION ALL SELECT '2日DDE', 11, 'dde-combo', 'algorithm/ddeCombo', '{"title":"2日DDE算法"}', 'AlgorithmDdeCombo'
    UNION ALL SELECT 'DDE资金30', 12, 'dde-top30', 'algorithm/ddeTop30', '{"title":"DDE资金30算法"}', 'AlgorithmDdeTop30'
    UNION ALL SELECT 'DDE热度榜', 13, 'dde-hot-rank', 'algorithm/ddeHotRank', '{"title":"DDE热度算法"}', 'AlgorithmDdeHotRank'
    UNION ALL SELECT 'DDE日内连续', 16, 'dde-intraday-combo', 'algorithm/ddeObservation', '{"title":"DDE日内连续算法"}', 'AlgorithmDdeIntraday'
    UNION ALL SELECT '主连资金', 20, 'main-fund', 'algorithm/mainFund', '{"title":"主连资金算法"}', 'AlgorithmMainFund'
    UNION ALL SELECT '融资融券', 30, 'margin-trading', 'algorithm/marginTrading', '{"title":"融资融券算法"}', 'AlgorithmMargin'
    UNION ALL SELECT '融资2天', 31, 'margin-2d', 'algorithm/marginTrading', '{"title":"融资2天算法","windowDays":2}', 'AlgorithmMargin2d'
    UNION ALL SELECT '融资3天', 32, 'margin-3d', 'algorithm/marginTrading', '{"title":"融资3天算法","windowDays":3}', 'AlgorithmMargin3d'
    UNION ALL SELECT '融资5天', 33, 'margin-5d', 'algorithm/marginTrading', '{"title":"融资5天算法","windowDays":5}', 'AlgorithmMargin5d'
    UNION ALL SELECT 'KDJ', 34, 'kdj', 'algorithm/kdj', '{"title":"KDJ算法"}', 'AlgorithmKdj'
) AS menus
WHERE @algorithm_menu_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE parent_id = @algorithm_menu_id AND sys_menu.menu_name = menus.menu_name AND menu_type = 'C');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu
WHERE menu_id = @algorithm_menu_id OR parent_id = @algorithm_menu_id
  AND NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id);

COMMIT;
