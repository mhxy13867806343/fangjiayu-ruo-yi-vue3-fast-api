-- 导入菜单数据
USE `ruoyi-fastapi`;

-- 导入菜单-角色关联数据
INSERT INTO sys_role_menu SELECT '1', menu_id FROM sys_menu;
