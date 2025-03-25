-- 轮播图表
CREATE TABLE sys_carousel (
  id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '轮播图ID',
  title varchar(100) NOT NULL COMMENT '标题',
  type char(1) NOT NULL COMMENT '轮播类型（1普通轮播 2活动轮播 3推广轮播）',
  category char(1) NOT NULL COMMENT '分类（1活动 2促销 3新品 4热门 5推荐）',
  position char(1) NOT NULL COMMENT '显示位置（1首页 0其他页面）',
  url varchar(255) DEFAULT NULL COMMENT 'URL地址',
  is_external_link char(1) DEFAULT '0' COMMENT '是否外部链接（0否 1是）',
  start_time datetime DEFAULT NULL COMMENT '开始时间',
  end_time datetime DEFAULT NULL COMMENT '结束时间',
  detail text COMMENT '详情信息',
  status char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
  sort int(4) DEFAULT 0 COMMENT '排序',
  create_by varchar(64) DEFAULT '' COMMENT '创建者',
  create_time datetime DEFAULT NULL COMMENT '创建时间',
  update_by varchar(64) DEFAULT '' COMMENT '更新者',
  update_time datetime DEFAULT NULL COMMENT '更新时间',
  remark varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='轮播图表';

-- 轮播图媒体表
CREATE TABLE sys_carousel_media (
  id bigint(20) NOT NULL AUTO_INCREMENT COMMENT '媒体ID',
  carousel_id bigint(20) NOT NULL COMMENT '轮播图ID',
  name varchar(100) NOT NULL COMMENT '媒体名称',
  type char(10) NOT NULL COMMENT '媒体类型（image图片 video视频）',
  url varchar(255) NOT NULL COMMENT '媒体URL',
  external_link varchar(255) DEFAULT NULL COMMENT '外链地址',
  sort int(4) DEFAULT 0 COMMENT '排序',
  create_by varchar(64) DEFAULT '' COMMENT '创建者',
  create_time datetime DEFAULT NULL COMMENT '创建时间',
  update_by varchar(64) DEFAULT '' COMMENT '更新者',
  update_time datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_carousel_id (carousel_id)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='轮播图媒体表';

-- 字典类型数据
INSERT INTO sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) 
VALUES (100, '轮播类型', 'sys_carousel_type', '0', 'admin', NOW(), '', NULL, '轮播类型列表');

INSERT INTO sys_dict_type (dict_id, dict_name, dict_type, status, create_by, create_time, update_by, update_time, remark) 
VALUES (101, '活动分类', 'sys_category', '0', 'admin', NOW(), '', NULL, '活动分类列表');

-- 字典数据
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1001, 1, '普通轮播', '1', 'sys_carousel_type', '', 'default', 'Y', '0', 'admin', NOW(), '', NULL, '');
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1002, 2, '活动轮播', '2', 'sys_carousel_type', '', 'success', 'N', '0', 'admin', NOW(), '', NULL, '');
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1003, 3, '推广轮播', '3', 'sys_carousel_type', '', 'warning', 'N', '0', 'admin', NOW(), '', NULL, '');

INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1101, 1, '活动', '1', 'sys_category', '', 'primary', 'Y', '0', 'admin', NOW(), '', NULL, '');
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1102, 2, '促销', '2', 'sys_category', '', 'success', 'N', '0', 'admin', NOW(), '', NULL, '');
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1103, 3, '新品', '3', 'sys_category', '', 'info', 'N', '0', 'admin', NOW(), '', NULL, '');
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1104, 4, '热门', '4', 'sys_category', '', 'warning', 'N', '0', 'admin', NOW(), '', NULL, '');
INSERT INTO sys_dict_data (dict_code, dict_sort, dict_label, dict_value, dict_type, css_class, list_class, is_default, status, create_by, create_time, update_by, update_time, remark) 
VALUES (1105, 5, '推荐', '5', 'sys_category', '', 'danger', 'N', '0', 'admin', NOW(), '', NULL, '');
