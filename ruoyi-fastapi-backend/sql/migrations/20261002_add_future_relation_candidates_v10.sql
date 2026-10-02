INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('原油', 'positive', 'overseas', 'NYMEX', 'FC.CL', 'CL', 'domestic', 'XSGE', 'FC.PITCH', 'BU', 110, '沥青石化上游，待人工验证'),
    ('原油', 'positive', 'overseas', 'NYMEX', 'FC.CL', 'CL', 'domestic', 'XZCE', 'FC.PX', 'PX', 111, '对二甲苯石化上游，待人工验证'),
    ('原油', 'positive', 'overseas', 'NYMEX', 'FC.CL', 'CL', 'domestic', 'XDCE', 'FC.BZ', 'BZ', 112, '纯苯石化上游，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
