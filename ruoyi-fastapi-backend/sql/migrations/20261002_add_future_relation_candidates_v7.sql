INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('玉米', 'inverse', 'domestic', 'XDCE', 'FC.CORN', 'C', 'domestic', 'XDCE', 'FC.EGG', 'JD', 80, '饲料成本与蛋鸡养殖利润，待人工验证'),
    ('豆粕', 'inverse', 'domestic', 'XDCE', 'FC.BEAN', 'M', 'domestic', 'XDCE', 'FC.EGG', 'JD', 81, '饲料成本与蛋鸡养殖利润，待人工验证'),
    ('铁矿石', 'positive', 'domestic', 'XDCE', 'FC.INRU', 'I', 'domestic', 'XSGE', 'FC.COIL', 'HC', 82, '热卷炼钢原料链，待人工验证'),
    ('焦炭', 'positive', 'domestic', 'XDCE', 'FC.COKE', 'J', 'domestic', 'XSGE', 'FC.REBAR', 'RB', 83, '炼钢燃料链，待人工验证'),
    ('硅铁', 'similar', 'domestic', 'XZCE', 'FC.METAL', 'SF', 'domestic', 'XZCE', 'FC.METAL', 'SM', 84, '钢铁合金添加剂，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
