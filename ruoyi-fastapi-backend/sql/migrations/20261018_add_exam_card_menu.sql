INSERT INTO sys_menu(menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT '考试',0,50,'exam','Layout','','Exam',1,0,'M','0','0','','education','admin',CURRENT_TIMESTAMP,'admin',CURRENT_TIMESTAMP,'知识卡片与复习'
WHERE NOT EXISTS(SELECT 1 FROM sys_menu WHERE parent_id=0 AND path='exam');

INSERT INTO sys_menu(menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
SELECT 'Java 知识卡片',menu_id,1,'java-cards','exam/cards','','ExamJavaCards',1,0,'C','0','0','exam:card:list','collection','admin',CURRENT_TIMESTAMP,'admin',CURRENT_TIMESTAMP,'Java 面试知识卡片库'
FROM sys_menu parent_menu
WHERE parent_menu.parent_id=0 AND parent_menu.path='exam'
AND NOT EXISTS(SELECT 1 FROM sys_menu WHERE parent_id=parent_menu.menu_id AND path='java-cards');

INSERT INTO sys_role_menu(role_id,menu_id)
SELECT 1,menu_id FROM sys_menu WHERE perms='exam:card:list'
AND NOT EXISTS(SELECT 1 FROM sys_role_menu x WHERE x.role_id=1 AND x.menu_id=sys_menu.menu_id);
