DROP TABLE IF EXISTS t_stock_dde_user_mark;

ALTER TABLE t_stock_dde_signal ADD COLUMN is_marked INTEGER NOT NULL DEFAULT 0;
