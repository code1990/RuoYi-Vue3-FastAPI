INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('豆油', 'similar', 'domestic', 'XDCE', 'FC.BOIL', 'Y', 'domestic', 'XDCE', 'FC.PALM', 'P', 30, '可替代植物油，待人工验证'),
    ('菜油', 'similar', 'domestic', 'XZCE', 'FC.MEAL', 'OI', 'domestic', 'XDCE', 'FC.PALM', 'P', 31, '可替代植物油，待人工验证'),
    ('豆粕', 'similar', 'domestic', 'XDCE', 'FC.BEAN', 'M', 'domestic', 'XZCE', 'FC.MEAL', 'RM', 32, '可替代蛋白粕，待人工验证'),
    ('铁矿石', 'positive', 'domestic', 'XDCE', 'FC.INRU', 'I', 'domestic', 'XDCE', 'FC.COKE', 'J', 33, '炼钢原料链，待人工验证'),
    ('焦煤', 'positive', 'domestic', 'XDCE', 'FC.COAL', 'JM', 'domestic', 'XDCE', 'FC.COKE', 'J', 34, '焦化原料链，待人工验证'),
    ('螺纹钢', 'similar', 'domestic', 'XSGE', 'FC.REBAR', 'RB', 'domestic', 'XSGE', 'FC.COIL', 'HC', 35, '钢材同类需求，待人工验证'),
    ('玻璃', 'positive', 'domestic', 'XZCE', 'FC.GLASS', 'FG', 'domestic', 'XZCE', 'FC.GLASS', 'SA', 36, '纯碱为玻璃原料，待人工验证'),
    ('天然橡胶', 'similar', 'domestic', 'XSGE', 'FC.RUBBER', 'RU', 'domestic', 'XSGE', 'FC.BR', 'BR', 37, '合成与天然橡胶替代，待人工验证'),
    ('塑料', 'similar', 'domestic', 'XDCE', 'FC.PETR', 'L', 'domestic', 'XDCE', 'FC.PETR', 'V', 38, '通用树脂替代，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
