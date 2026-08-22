-- Quant backtest menu ordering. Safe to run repeatedly.

START TRANSACTION;

SET @quant_menu_id := (
    SELECT menu_id FROM sys_menu WHERE parent_id = 0 AND menu_name = '量化回测' AND menu_type = 'M' LIMIT 1
);

UPDATE sys_menu
SET order_num = CASE menu_name
    WHEN 'DDE资金' THEN 10
    WHEN '2日DDE' THEN 11
    WHEN '主连资金' THEN 20
    WHEN '融资融券' THEN 30
    WHEN '融资2天' THEN 31
    WHEN '融资3天' THEN 32
    WHEN '融资5天' THEN 33
END,
update_by = 'admin',
update_time = NOW()
WHERE parent_id = @quant_menu_id
  AND menu_type = 'C'
  AND menu_name IN ('DDE资金', '2日DDE', '主连资金', '融资融券', '融资2天', '融资3天', '融资5天');

COMMIT;
