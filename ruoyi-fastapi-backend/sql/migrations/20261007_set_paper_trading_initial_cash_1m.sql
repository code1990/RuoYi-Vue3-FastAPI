ALTER TABLE future_paper_account ALTER cash SET DEFAULT 1000000;
ALTER TABLE future_paper_account ALTER initial_cash SET DEFAULT 1000000;

UPDATE future_paper_account
SET cash = 1000000, initial_cash = 1000000
WHERE cash = 2000000 AND initial_cash = 2000000;
