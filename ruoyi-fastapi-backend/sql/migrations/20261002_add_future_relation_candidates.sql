ALTER TABLE t_future_product_link
    ADD COLUMN review_status ENUM('pending', 'confirmed', 'rejected') NOT NULL DEFAULT 'pending' COMMENT '人工审核状态' AFTER remark;

INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('原油', 'similar', 'overseas', 'NYMEX', 'FC.CL', 'CL', 'overseas', 'NYMEX', 'FC.BZ', 'BZ', 20, 'WTI 与布伦特原油基准，待人工验证'),
    ('原油', 'positive', 'overseas', 'NYMEX', 'FC.CL', 'CL', 'overseas', 'NYMEX', 'FC.HO', 'HO', 21, '原油与燃油产业链，待人工验证'),
    ('原油', 'positive', 'overseas', 'NYMEX', 'FC.CL', 'CL', 'overseas', 'NYMEX', 'FC.RB', 'RB', 22, '原油与汽油产业链，待人工验证'),
    ('燃油', 'similar', 'domestic', 'XSGE', 'FC.FUEL', 'FU', 'overseas', 'NYMEX', 'FC.HO', 'HO', 23, '国内燃油与 NYMEX 燃油，待人工验证'),
    ('燃油', 'positive', 'domestic', 'XSGE', 'FC.FUEL', 'FU', 'overseas', 'NYMEX', 'FC.CL', 'CL', 24, '燃油与原油产业链，待人工验证'),
    ('铁矿石', 'positive', 'domestic', 'XDCE', 'FC.INRU', 'I', 'domestic', 'XSGE', 'FC.REBAR', 'RB', 25, '炼钢产业链，待人工验证'),
    ('焦煤', 'positive', 'domestic', 'XDCE', 'FC.COAL', 'JM', 'domestic', 'XSGE', 'FC.REBAR', 'RB', 26, '炼钢产业链，待人工验证')
ON DUPLICATE KEY UPDATE relation_type = VALUES(relation_type), remark = VALUES(remark);
