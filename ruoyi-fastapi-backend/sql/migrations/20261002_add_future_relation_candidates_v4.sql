INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('玉米', 'inverse', 'domestic', 'XDCE', 'FC.CORN', 'C', 'domestic', 'XDCE', 'FC.LH', 'LH', 50, '饲料成本与生猪养殖利润，待人工验证'),
    ('棉花', 'positive', 'domestic', 'XZCE', 'FC.COTTON', 'CF', 'domestic', 'XZCE', 'FC.COTTON', 'CY', 51, '棉纱原料，待人工验证'),
    ('氧化铝', 'positive', 'domestic', 'XSGE', 'FC.AO', 'AO', 'domestic', 'XSGE', 'FC.METAL', 'AL', 52, '电解铝原料，待人工验证'),
    ('沪镍', 'positive', 'domestic', 'XSGE', 'FC.NiSn', 'NI', 'domestic', 'XSGE', 'FC.METAL', 'SS', 53, '不锈钢原料，待人工验证'),
    ('工业硅', 'positive', 'domestic', 'XGFE', 'FC.SI', 'SI', 'domestic', 'XGFE', 'FC.PS', 'PS', 54, '多晶硅原料，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
