ALTER TABLE future_paper_order ADD COLUMN exchange_fee DOUBLE NOT NULL DEFAULT 0 AFTER fee;
ALTER TABLE future_paper_order ADD COLUMN broker_fee DOUBLE NOT NULL DEFAULT 0 AFTER exchange_fee;
