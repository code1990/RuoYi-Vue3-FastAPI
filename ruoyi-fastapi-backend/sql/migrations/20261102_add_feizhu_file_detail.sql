CREATE TABLE IF NOT EXISTS t_file_detail (
  id varchar(32) NOT NULL COMMENT '唯一id', topic varchar(255) NOT NULL COMMENT '主题', eu varchar(255) NOT NULL COMMENT 'eu', filename varchar(255) DEFAULT NULL COMMENT '文件名', size varchar(255) DEFAULT NULL COMMENT '文件大小', ctime datetime DEFAULT NULL COMMENT '创建时间', utime datetime DEFAULT NULL COMMENT '更新时间', ext varchar(32) DEFAULT '2' COMMENT '文件类型', category int(4) DEFAULT NULL COMMENT '类别', user varchar(32) DEFAULT NULL COMMENT '用户', type varchar(32) DEFAULT NULL COMMENT 'url类型', file_list text DEFAULT NULL COMMENT '文件列表', url varchar(255) DEFAULT NULL COMMENT '文件地址', pwd varchar(255) DEFAULT NULL COMMENT '文件密码', haspwd varchar(255) DEFAULT NULL COMMENT '文件是否加密', valid varchar(255) DEFAULT NULL COMMENT '文件是否可用', create_by varchar(64) DEFAULT '' COMMENT '创建者', create_time datetime DEFAULT NULL COMMENT '创建时间', update_by varchar(64) DEFAULT '' COMMENT '更新者', update_time datetime DEFAULT NULL COMMENT '更新时间', remark varchar(500) DEFAULT '' COMMENT '备注', PRIMARY KEY (id), KEY idx_file_detail_topic (topic)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文件资源';

CREATE TABLE IF NOT EXISTS t_file_keyword (
  id varchar(32) NOT NULL COMMENT '唯一ID', keyword varchar(255) NOT NULL COMMENT '关键字', sort_no int NOT NULL DEFAULT 0 COMMENT '排序', create_by varchar(64) DEFAULT '' COMMENT '创建者', create_time datetime DEFAULT NULL COMMENT '创建时间', update_by varchar(64) DEFAULT '' COMMENT '更新者', update_time datetime DEFAULT NULL COMMENT '更新时间', remark varchar(500) DEFAULT '' COMMENT '备注', PRIMARY KEY (id), UNIQUE KEY uk_file_keyword_keyword (keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪盘关键字';

CREATE TABLE IF NOT EXISTS t_file_keyword_topic (
  id varchar(32) NOT NULL COMMENT '唯一ID', keyword_id varchar(32) NOT NULL COMMENT '关键字ID', topic varchar(255) NOT NULL COMMENT '主题', sort_no int NOT NULL DEFAULT 0 COMMENT '排序', create_by varchar(64) DEFAULT '' COMMENT '创建者', create_time datetime DEFAULT NULL COMMENT '创建时间', update_by varchar(64) DEFAULT '' COMMENT '更新者', update_time datetime DEFAULT NULL COMMENT '更新时间', PRIMARY KEY (id), UNIQUE KEY uk_file_keyword_topic (keyword_id, topic), KEY idx_file_keyword_topic_keyword_id (keyword_id), KEY idx_file_keyword_topic_topic (topic)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪盘关键字主题关联';

INSERT INTO sys_menu(menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '文件明细',0,60,'file-detail','feizhu/file-detail','','FeizhuFileDetail',1,0,'C','0','0','feizhu:file-detail:list','files','admin',NOW(),'admin',NOW(),'飞猪盘文件检索'
WHERE NOT EXISTS(SELECT 1 FROM sys_menu WHERE parent_id=0 AND path='file-detail');

INSERT INTO sys_role_menu(role_id,menu_id)
SELECT 1,menu_id FROM sys_menu WHERE parent_id=0 AND path='file-detail'
AND NOT EXISTS(SELECT 1 FROM sys_role_menu x WHERE x.role_id=1 AND x.menu_id=sys_menu.menu_id);
