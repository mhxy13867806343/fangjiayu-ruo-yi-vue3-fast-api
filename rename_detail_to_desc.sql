-- 将detail字段重命名为desc
ALTER TABLE `sys_carousel` CHANGE COLUMN `detail` `desc` TEXT NULL COMMENT '详情内容';
