CREATE TABLE IF NOT EXISTS future_paper_daily_mark (
  mark_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  position_id BIGINT NOT NULL,
  contract_code VARCHAR(40) NOT NULL,
  trade_date DATE NOT NULL,
  mark_price DOUBLE NOT NULL,
  floating_pnl DOUBLE NOT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_future_paper_daily_mark (user_id, position_id, trade_date),
  KEY idx_future_paper_daily_mark_user_date (user_id, trade_date)
);
