ALTER TABLE t_future_product_link
    ADD COLUMN relation_type ENUM('positive', 'inverse', 'similar') NOT NULL DEFAULT 'similar' COMMENT '正向、反向或相似' AFTER group_name;
