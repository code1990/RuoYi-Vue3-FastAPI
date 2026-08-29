DELETE role_menu
FROM sys_role_menu AS role_menu
JOIN sys_menu AS menu ON menu.menu_id = role_menu.menu_id
WHERE menu.parent_id = 2053;

DELETE FROM sys_menu WHERE parent_id = 2053;

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES
  ('平量', 2053, 1, '1', 'stock/pool/stock', '{"formulaId":"1"}', 'StockPoolFormula1', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=1'),
  ('建仓买点', 2053, 2, '2', 'stock/pool/stock', '{"formulaId":"2"}', 'StockPoolFormula2', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=2'),
  ('最佳买入时机', 2053, 3, '3', 'stock/pool/stock', '{"formulaId":"3"}', 'StockPoolFormula3', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=3'),
  ('进攻买', 2053, 4, '4', 'stock/pool/stock', '{"formulaId":"4"}', 'StockPoolFormula4', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=4'),
  ('共振买', 2053, 5, '5', 'stock/pool/stock', '{"formulaId":"5"}', 'StockPoolFormula5', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=5'),
  ('双K', 2053, 6, '6', 'stock/pool/stock', '{"formulaId":"6"}', 'StockPoolFormula6', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=6'),
  ('单K', 2053, 7, '7', 'stock/pool/stock', '{"formulaId":"7"}', 'StockPoolFormula7', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=7'),
  ('K11买', 2053, 8, '8', 'stock/pool/stock', '{"formulaId":"8"}', 'StockPoolFormula8', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=8'),
  ('右侧牛股', 2053, 9, '9', 'stock/pool/stock', '{"formulaId":"9"}', 'StockPoolFormula9', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=9'),
  ('J_MACD共振买', 2053, 10, '16', 'stock/pool/stock', '{"formulaId":"16"}', 'StockPoolFormula16', 1, 0, 'C', '0', '0', 'stock:pools:list', 'money', 'admin', NOW(), 'admin', NOW(), 't_stock_formula.id=16');

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE parent_id = 2053;
