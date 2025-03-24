-- 更新所有用户的密码为系统默认密码
UPDATE `ruoyi-fastapi`.sys_user SET password='$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2' WHERE del_flag='0';
