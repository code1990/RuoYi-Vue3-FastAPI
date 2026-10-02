INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('对二甲苯', 'positive', 'domestic', 'XZCE', 'FC.PX', 'PX', 'domestic', 'XZCE', 'FC.PTA', 'TA', 40, 'PTA 上游原料，待人工验证'),
    ('PTA', 'positive', 'domestic', 'XZCE', 'FC.PTA', 'TA', 'domestic', 'XDCE', 'FC.EG', 'EG', 41, '聚酯双原料，待人工验证'),
    ('PTA', 'positive', 'domestic', 'XZCE', 'FC.PTA', 'TA', 'domestic', 'XZCE', 'FC.PTA', 'PF', 42, '涤纶短纤原料，待人工验证'),
    ('乙二醇', 'positive', 'domestic', 'XDCE', 'FC.EG', 'EG', 'domestic', 'XZCE', 'FC.PTA', 'PF', 43, '涤纶短纤原料，待人工验证'),
    ('甲醇', 'positive', 'domestic', 'XZCE', 'FC.MA', 'MA', 'domestic', 'XDCE', 'FC.PETR', 'PP', 44, 'MTO 工艺原料，待人工验证'),
    ('PP', 'similar', 'domestic', 'XDCE', 'FC.PETR', 'PP', 'domestic', 'XDCE', 'FC.PETR', 'L', 45, '通用树脂替代，待人工验证'),
    ('大豆', 'positive', 'domestic', 'XDCE', 'FC.BEAN', 'A', 'domestic', 'XDCE', 'FC.BEAN', 'M', 46, '大豆压榨蛋白粕，待人工验证'),
    ('大豆', 'positive', 'domestic', 'XDCE', 'FC.BEAN', 'A', 'domestic', 'XDCE', 'FC.BOIL', 'Y', 47, '大豆压榨油脂，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
