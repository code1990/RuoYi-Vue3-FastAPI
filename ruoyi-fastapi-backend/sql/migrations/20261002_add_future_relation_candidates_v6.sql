INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('纯苯', 'positive', 'domestic', 'XDCE', 'FC.BZ', 'BZ', 'domestic', 'XDCE', 'FC.PETR', 'EB', 70, '苯乙烯上游原料，待人工验证'),
    ('PVC', 'inverse', 'domestic', 'XDCE', 'FC.PETR', 'V', 'domestic', 'XZCE', 'FC.SH', 'SH', 71, '氯碱联产关系，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
