-- Remove the temporary KDJ entry from Quant Statistics.

START TRANSACTION;

SET @stat_kdj_menu_id := (
    SELECT menu_id FROM sys_menu
    WHERE route_name = 'StatKdj' AND menu_type = 'C'
    LIMIT 1
);

DELETE FROM sys_role_menu
WHERE menu_id = @stat_kdj_menu_id;

DELETE FROM sys_menu
WHERE menu_id = @stat_kdj_menu_id;

COMMIT;
