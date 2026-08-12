-- Local/remote RuoYi MySQL migration: Quant backtest -> DDE fund menu.
-- Safe to run repeatedly; assigns the menu to the administrator role (role_id = 1).

START TRANSACTION;

SET @quant_menu_id := (
    SELECT menu_id
    FROM sys_menu
    WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M'
    LIMIT 1
);

INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
)
SELECT
    '量化回测', 0, 6, 'quant', 'Layout', '', 'Quant',
    1, 0, 'M', '0', '0', '', 'chart',
    'admin', NOW(), 'admin', NOW(), '量化回测'
WHERE @quant_menu_id IS NULL;

SET @quant_menu_id := COALESCE(
    @quant_menu_id,
    (SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1)
);

SET @dde_menu_id := (
    SELECT menu_id
    FROM sys_menu
    WHERE parent_id = @quant_menu_id AND menu_name = 'DDE资金' AND menu_type = 'C'
    LIMIT 1
);

INSERT INTO sys_menu (
    menu_name, parent_id, order_num, path, component, query, route_name,
    is_frame, is_cache, menu_type, visible, status, perms, icon,
    create_by, create_time, update_by, update_time, remark
)
SELECT
    'DDE资金', @quant_menu_id, 1, 'dde', 'stock/ddeFund', '', 'DdeFund',
    1, 0, 'C', '0', '0', 'stock:dde:list', 'money',
    'admin', NOW(), 'admin', NOW(), 'DDE资金流'
WHERE @dde_menu_id IS NULL;

SET @dde_menu_id := COALESCE(
    @dde_menu_id,
    (SELECT menu_id FROM sys_menu WHERE parent_id = @quant_menu_id AND menu_name = 'DDE资金' AND menu_type = 'C' LIMIT 1)
);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @quant_menu_id
WHERE NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @quant_menu_id);

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, @dde_menu_id
WHERE NOT EXISTS (SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND menu_id = @dde_menu_id);

COMMIT;
