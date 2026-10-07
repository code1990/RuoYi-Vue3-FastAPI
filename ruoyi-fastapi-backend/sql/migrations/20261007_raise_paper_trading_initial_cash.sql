ALTER TABLE future_paper_account ALTER cash SET DEFAULT 2000000;
ALTER TABLE future_paper_account ALTER initial_cash SET DEFAULT 2000000;

UPDATE future_paper_account a
LEFT JOIN future_paper_position p ON p.user_id = a.user_id
SET a.cash = 2000000, a.initial_cash = 2000000
WHERE a.cash = 100000 AND a.initial_cash = 100000 AND p.user_id IS NULL;
