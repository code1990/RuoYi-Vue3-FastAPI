CREATE TABLE IF NOT EXISTS t_stock_dde_user_mark (
    user_id INTEGER NOT NULL,
    stock_code TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    signal_slot TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, stock_code, trade_date, signal_slot)
);

CREATE INDEX IF NOT EXISTS idx_stock_dde_user_mark_user_date
    ON t_stock_dde_user_mark (user_id, trade_date);
