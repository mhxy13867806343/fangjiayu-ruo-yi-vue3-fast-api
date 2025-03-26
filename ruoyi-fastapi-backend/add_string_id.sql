-- 为 h5_user 表添加 string_id 字段
ALTER TABLE h5_user ADD COLUMN string_id VARCHAR(30) UNIQUE COMMENT '字符串用户ID';

-- 更新现有用户的 string_id 字段（这里使用一个简单的格式：'USER' + user_id）
-- 实际应用中，您可能需要使用更复杂的逻辑来生成唯一的 string_id
UPDATE h5_user SET string_id = CONCAT('USER', LPAD(user_id, 26, '0')) WHERE string_id IS NULL;
