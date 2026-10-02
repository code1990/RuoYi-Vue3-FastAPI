INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('黄金', 'similar', 'domestic', 'XSGE', 'FC.GOLD', 'AU', 'domestic', 'XSGE', 'FC.SILVER', 'AG', 90, '贵金属避险与货币属性，待人工验证'),
    ('铂', 'similar', 'domestic', 'XGFE', 'FC.PT', 'PT', 'domestic', 'XGFE', 'FC.PD', 'PD', 91, '铂族金属需求，待人工验证'),
    ('沪铜', 'similar', 'domestic', 'XSGE', 'FC.METAL', 'CU', 'domestic', 'XSGE', 'FC.METAL', 'AL', 92, '基本金属宏观需求，待人工验证'),
    ('沪铝', 'similar', 'domestic', 'XSGE', 'FC.METAL', 'AL', 'domestic', 'XSGE', 'FC.METAL', 'ZN', 93, '基本金属宏观需求，待人工验证'),
    ('沪铜', 'similar', 'domestic', 'XSGE', 'FC.METAL', 'CU', 'domestic', 'XSGE', 'FC.METAL', 'ZN', 94, '基本金属宏观需求，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
