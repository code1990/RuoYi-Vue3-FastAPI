CREATE TABLE IF NOT EXISTS future_paper_account (
  user_id BIGINT NOT NULL PRIMARY KEY,
  cash DOUBLE NOT NULL DEFAULT 100000,
  initial_cash DOUBLE NOT NULL DEFAULT 100000,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS future_paper_position (
  position_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  contract_code VARCHAR(40) NOT NULL,
  contract_name VARCHAR(100) NOT NULL DEFAULT '',
  side VARCHAR(4) NOT NULL,
  quantity INT NOT NULL,
  average_price DOUBLE NOT NULL,
  multiplier DOUBLE NOT NULL,
  margin DOUBLE NOT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_future_paper_position (user_id, contract_code, side)
);

CREATE TABLE IF NOT EXISTS future_paper_order (
  order_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  contract_code VARCHAR(40) NOT NULL,
  contract_name VARCHAR(100) NOT NULL DEFAULT '',
  side VARCHAR(4) NOT NULL,
  action VARCHAR(8) NOT NULL,
  quantity INT NOT NULL,
  price DOUBLE NOT NULL,
  realized_pnl DOUBLE NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_future_paper_order_user (user_id, order_id)
);

SET @future_menu_id := (SELECT menu_id FROM sys_menu WHERE parent_id=0 AND path='future' AND menu_type='M' LIMIT 1);
INSERT INTO sys_menu(menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '模拟交易',@future_menu_id,1,'paper-trading','future/paper-trading','','FuturePaperTrading',1,0,'C','0','0','future:paper-trading:list','money','admin',NOW(),'admin',NOW(),'线上模拟期货交易'
WHERE @future_menu_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM sys_menu WHERE parent_id=@future_menu_id AND path='paper-trading');
INSERT INTO sys_role_menu(role_id,menu_id)
SELECT 1,menu_id FROM sys_menu WHERE parent_id=@future_menu_id AND path='paper-trading'
AND NOT EXISTS(SELECT 1 FROM sys_role_menu x WHERE x.role_id=1 AND x.menu_id=sys_menu.menu_id);
