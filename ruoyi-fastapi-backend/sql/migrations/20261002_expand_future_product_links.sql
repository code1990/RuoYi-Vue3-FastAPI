ALTER TABLE t_future_product_link
    DROP INDEX uk_future_product_link,
    CHANGE COLUMN scope source_scope VARCHAR(10) NOT NULL COMMENT '来源 domestic or overseas',
    ADD COLUMN contract_prefix VARCHAR(16) NOT NULL DEFAULT '' COMMENT '来源合约代码前缀' AFTER product_code,
    ADD COLUMN related_scope VARCHAR(10) NOT NULL COMMENT '关联 domestic or overseas' AFTER contract_prefix,
    ADD COLUMN related_market_code VARCHAR(10) NOT NULL AFTER related_scope,
    ADD COLUMN related_product_code VARCHAR(32) NOT NULL AFTER related_market_code,
    ADD COLUMN related_contract_prefix VARCHAR(16) NOT NULL DEFAULT '' COMMENT '关联合约代码前缀' AFTER related_product_code,
    ADD COLUMN remark VARCHAR(255) NOT NULL DEFAULT '' AFTER sort_order,
    ADD UNIQUE KEY uk_future_product_relation (market_code, product_code, contract_prefix, related_market_code, related_product_code, related_contract_prefix);

DELETE FROM t_future_product_link;

INSERT INTO t_future_product_link (group_name, relation_type, source_scope, market_code, product_code, contract_prefix, related_scope, related_market_code, related_product_code, related_contract_prefix, sort_order, remark) VALUES
    ('黄金', 'similar', 'domestic', 'XSGE', 'FC.GOLD', 'AU', 'overseas', 'COMEX', 'FC.GC', 'GC', 1, '同一贵金属标的'),
    ('白银', 'similar', 'domestic', 'XSGE', 'FC.SILVER', 'AG', 'overseas', 'COMEX', 'FC.SI', 'SI', 2, '同一贵金属标的'),
    ('钯', 'similar', 'domestic', 'XGFE', 'FC.PD', 'PD', 'overseas', 'NYMEX', 'FC.PA', 'PA', 3, '同一贵金属标的'),
    ('铂', 'similar', 'domestic', 'XGFE', 'FC.PT', 'PT', 'overseas', 'NYMEX', 'FC.PL', 'PL', 4, '同一贵金属标的'),
    ('玉米', 'similar', 'domestic', 'XDCE', 'FC.CORN', 'C', 'overseas', 'CBOT', 'FC.ZC', 'ZC', 5, '同一农产品标的'),
    ('豆油', 'similar', 'domestic', 'XDCE', 'FC.BOIL', 'Y', 'overseas', 'CBOT', 'FC.ZL', 'ZL', 6, '同一油脂标的'),
    ('豆油', 'similar', 'domestic', 'XDCE', 'FC.BOIL', 'Y', 'domestic', 'XZCE', 'FC.MEAL', 'OI', 7, '可替代植物油'),
    ('豆粕', 'similar', 'domestic', 'XDCE', 'FC.BEAN', 'M', 'overseas', 'CBOT', 'FC.ZM', 'ZM', 8, '同一蛋白粕标的'),
    ('豆粕', 'inverse', 'domestic', 'XDCE', 'FC.BEAN', 'M', 'domestic', 'XDCE', 'FC.LH', 'LH', 9, '饲料成本与生猪养殖利润'),
    ('铁矿石', 'positive', 'domestic', 'XDCE', 'FC.INRU', 'I', 'domestic', 'XDCE', 'FC.COAL', 'JM', 10, '炼钢原料需求'),
    ('粳稻', 'similar', 'domestic', 'XZCE', 'FC.RICE', 'JR', 'overseas', 'CBOT', 'FC.ZR', 'ZR', 11, '同类谷物标的'),
    ('强麦', 'similar', 'domestic', 'XZCE', 'FC.WHEAT', 'WH', 'overseas', 'CBOT', 'FC.ZW', 'ZW', 12, '同类谷物标的');
