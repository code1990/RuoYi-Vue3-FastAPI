CREATE TABLE IF NOT EXISTS t_future_product_link (
    link_id BIGINT NOT NULL AUTO_INCREMENT,
    group_name VARCHAR(50) NOT NULL COMMENT '页面展示品种',
    scope VARCHAR(10) NOT NULL COMMENT 'domestic or overseas',
    market_code VARCHAR(10) NOT NULL,
    product_code VARCHAR(32) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    PRIMARY KEY (link_id),
    UNIQUE KEY uk_future_product_link (group_name, market_code, product_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='国内外期货品种关联';

INSERT INTO t_future_product_link (group_name, scope, market_code, product_code, sort_order) VALUES
    ('黄金', 'domestic', 'XSGE', 'FC.GOLD', 1),
    ('黄金', 'overseas', 'COMEX', 'FC.GC', 2),
    ('白银', 'domestic', 'XSGE', 'FC.SILVER', 1),
    ('白银', 'overseas', 'COMEX', 'FC.SI', 2),
    ('钯', 'domestic', 'XGFE', 'FC.PD', 1),
    ('钯', 'overseas', 'NYMEX', 'FC.PA', 2),
    ('铂', 'domestic', 'XGFE', 'FC.PT', 1),
    ('铂', 'overseas', 'NYMEX', 'FC.PL', 2),
    ('玉米', 'domestic', 'XDCE', 'FC.CORN', 1),
    ('玉米', 'overseas', 'CBOT', 'FC.ZC', 2),
    ('豆油', 'domestic', 'XDCE', 'FC.BOIL', 1),
    ('豆油', 'overseas', 'CBOT', 'FC.ZL', 2),
    ('稻谷', 'domestic', 'XZCE', 'FC.RICE', 1),
    ('稻谷', 'overseas', 'CBOT', 'FC.ZR', 2),
    ('小麦', 'domestic', 'XZCE', 'FC.WHEAT', 1),
    ('小麦', 'overseas', 'CBOT', 'FC.ZW', 2)
ON DUPLICATE KEY UPDATE scope = VALUES(scope), sort_order = VALUES(sort_order);
