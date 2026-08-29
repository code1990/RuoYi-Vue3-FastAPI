UPDATE sys_menu
SET component = 'Layout', menu_type = 'M', update_time = NOW(), update_by = 'admin'
WHERE menu_id = 2053;

UPDATE sys_menu
SET component = 'stock/pool/stock', update_time = NOW(), update_by = 'admin'
WHERE parent_id = 2053;
