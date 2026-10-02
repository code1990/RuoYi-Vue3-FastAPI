INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('纸浆', 'positive', 'domestic', 'XSGE', 'FC.PULP', 'SP', 'domestic', 'XSGE', 'FC.OP', 'OP', 60, '胶版印刷纸原料，待人工验证'),
    ('棉花', 'similar', 'domestic', 'XZCE', 'FC.COTTON', 'CF', 'domestic', 'XZCE', 'FC.PTA', 'PF', 61, '纺织纤维替代，待人工验证'),
    ('燃油', 'positive', 'domestic', 'XSGE', 'FC.FUEL', 'FU', 'domestic', 'XSGE', 'FC.PITCH', 'BU', 62, '石油炼化产品，待人工验证'),
    ('LPG', 'positive', 'domestic', 'XDCE', 'FC.PG', 'PG', 'domestic', 'XSGE', 'FC.FUEL', 'FU', 63, '能源化工品，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
