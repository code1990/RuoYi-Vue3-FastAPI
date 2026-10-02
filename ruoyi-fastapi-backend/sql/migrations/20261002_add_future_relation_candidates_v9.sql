INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('烧碱', 'positive', 'domestic', 'XZCE', 'FC.SH', 'SH', 'domestic', 'XSGE', 'FC.AO', 'AO', 100, '氧化铝生产用碱，待人工验证'),
    ('动力煤', 'positive', 'domestic', 'XZCE', 'FC.STEAMCOAL', 'ZC', 'domestic', 'XGFE', 'FC.SI', 'SI', 101, '工业硅高耗电成本，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
