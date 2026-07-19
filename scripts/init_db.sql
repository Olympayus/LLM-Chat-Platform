-- ============================================================
-- 企业智能协同平台 - 数据库初始化脚本
-- MySQL 5.7.26+ / utf8mb4
-- ============================================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS llm_platform
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE llm_platform;

-- ============================================================
-- 以下为首次建表脚本，后续通过 Alembic 管理变更。
-- 首次搭建时执行此脚本，之后只用 alembic upgrade head。
-- ============================================================

-- 2. 用户与部门（F-01）
CREATE TABLE IF NOT EXISTS sys_dept (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '部门ID',
    parent_id BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '父部门ID',
    name VARCHAR(64) NOT NULL COMMENT '部门名称',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
    leader_id BIGINT UNSIGNED DEFAULT NULL COMMENT '负责人ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(64) NOT NULL COMMENT '用户名',
    password_hash VARCHAR(256) NOT NULL COMMENT '密码哈希',
    email VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    mobile VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    real_name VARCHAR(64) DEFAULT NULL COMMENT '真实姓名',
    avatar_url VARCHAR(512) DEFAULT NULL COMMENT '头像URL',
    dept_id BIGINT UNSIGNED DEFAULT NULL COMMENT '所属部门',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 1=正常 0=禁用 2=封号',
    is_online TINYINT NOT NULL DEFAULT 0 COMMENT '是否在线',
    last_login_at DATETIME DEFAULT NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(64) DEFAULT NULL COMMENT '最后登录IP',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    INDEX idx_dept_id (dept_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 3. AI 模型配置（F-02）
CREATE TABLE IF NOT EXISTS model_config (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    display_name VARCHAR(128) NOT NULL COMMENT '展示名称',
    category VARCHAR(32) NOT NULL COMMENT '分类: text/image/video/embedding',
    base_url VARCHAR(512) NOT NULL COMMENT 'API Base URL',
    api_key VARCHAR(512) NOT NULL COMMENT 'API Key',
    model_id VARCHAR(128) NOT NULL COMMENT '模型ID',
    is_default TINYINT NOT NULL DEFAULT 0 COMMENT '是否默认',
    is_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI模型配置表';

-- 4. 技能管理（F-05）
CREATE TABLE IF NOT EXISTS skill (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '技能名称',
    type VARCHAR(32) NOT NULL COMMENT '类型: function_call/skill_md',
    description TEXT NOT NULL COMMENT '技能描述',
    category VARCHAR(32) DEFAULT NULL COMMENT '分类标签',
    params_schema JSON DEFAULT NULL COMMENT '参数定义(JSON Schema)',
    python_code TEXT DEFAULT NULL COMMENT 'Function Call Python代码',
    skill_md_content TEXT DEFAULT NULL COMMENT 'SKILL.md内容',
    is_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_by BIGINT UNSIGNED DEFAULT NULL COMMENT '创建者',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技能表';

-- 5. 数字员工（F-06）
CREATE TABLE IF NOT EXISTS digital_employee (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '员工名称',
    avatar_url VARCHAR(512) DEFAULT NULL COMMENT '头像URL',
    role_description VARCHAR(256) DEFAULT NULL COMMENT '角色描述',
    model_id BIGINT UNSIGNED NOT NULL COMMENT '绑定模型ID',
    system_prompt TEXT NOT NULL COMMENT '系统提示词',
    temperature DECIMAL(3,2) DEFAULT 0.70 COMMENT '温度参数',
    max_tokens BIGINT UNSIGNED DEFAULT 4096 COMMENT '最大输出Token',
    is_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_by BIGINT UNSIGNED DEFAULT NULL COMMENT '创建者',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    INDEX idx_model_id (model_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数字员工表';

-- 6. 即时通讯（F-07）
CREATE TABLE IF NOT EXISTS im_group (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(128) NOT NULL COMMENT '群名称',
    avatar_url VARCHAR(512) DEFAULT NULL COMMENT '群头像',
    owner_id BIGINT UNSIGNED NOT NULL COMMENT '群主ID',
    notice VARCHAR(1024) DEFAULT NULL COMMENT '群公告',
    member_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '成员数',
    max_members INT UNSIGNED NOT NULL DEFAULT 500 COMMENT '成员上限',
    is_bot_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '允许数字员工应答',
    is_muted_all TINYINT NOT NULL DEFAULT 0 COMMENT '全员禁言',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=正常 0=已解散',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0,
    INDEX idx_owner_id (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='群组表';

CREATE TABLE IF NOT EXISTS im_message (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    chat_type VARCHAR(16) NOT NULL COMMENT 'private/group',
    sender_type VARCHAR(16) NOT NULL COMMENT 'user/bot',
    sender_id BIGINT UNSIGNED NOT NULL COMMENT '发送者ID',
    receiver_id BIGINT UNSIGNED DEFAULT NULL COMMENT '接收者ID(私聊)',
    group_id BIGINT UNSIGNED DEFAULT NULL COMMENT '群组ID(群聊)',
    msg_type VARCHAR(16) NOT NULL COMMENT 'text/image/file/voice/video/system',
    content TEXT NOT NULL COMMENT '消息内容',
    extra JSON DEFAULT NULL COMMENT '扩展字段',
    is_recalled TINYINT NOT NULL DEFAULT 0 COMMENT '是否撤回',
    recall_reason VARCHAR(256) DEFAULT NULL COMMENT '撤回原因',
    recalled_by BIGINT UNSIGNED DEFAULT NULL COMMENT '撤回操作人',
    is_read TINYINT NOT NULL DEFAULT 0 COMMENT '私聊已读',
    read_at DATETIME DEFAULT NULL COMMENT '已读时间',
    need_audit TINYINT NOT NULL DEFAULT 0 COMMENT '需审计标记',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_group_id_created (group_id, created_at),
    INDEX idx_sender_receiver (sender_id, receiver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';

-- 7. 群组与消息管理 / 合规（F-08）
CREATE TABLE IF NOT EXISTS im_sensitive_word (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(128) NOT NULL COMMENT '敏感词',
    level VARCHAR(16) NOT NULL COMMENT 'block/audit',
    category VARCHAR(32) DEFAULT NULL COMMENT '分类',
    is_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_by BIGINT UNSIGNED DEFAULT NULL COMMENT '创建者',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_word (word)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='敏感词库表';

-- 8. 爬虫与数据采集（F-04）
CREATE TABLE IF NOT EXISTS crawler_task (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '任务名称',
    request_url VARCHAR(1024) NOT NULL COMMENT '请求地址',
    request_method VARCHAR(8) NOT NULL DEFAULT 'GET' COMMENT '请求方法',
    request_headers JSON DEFAULT NULL COMMENT '请求头',
    request_body TEXT DEFAULT NULL COMMENT 'POST请求体',
    parse_rules JSON DEFAULT NULL COMMENT '解析规则',
    output_table VARCHAR(64) DEFAULT NULL COMMENT '入库目标表',
    schedule_cron VARCHAR(64) DEFAULT NULL COMMENT 'Cron表达式',
    is_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_by BIGINT UNSIGNED DEFAULT NULL COMMENT '创建者',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爬虫任务表';

-- 9. NL2SQL 智能问数（F-03）
CREATE TABLE IF NOT EXISTS nl2sql_query_history (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT '查询用户',
    question TEXT NOT NULL COMMENT '自然语言问题',
    generated_sql TEXT NOT NULL COMMENT '生成的SQL',
    is_valid TINYINT NOT NULL DEFAULT 0 COMMENT '安全校验是否通过',
    execution_time_ms INT UNSIGNED DEFAULT NULL COMMENT '执行耗时(ms)',
    result_rows INT UNSIGNED DEFAULT NULL COMMENT '返回行数',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='NL2SQL查询历史表';


-- ================================
-- 成员A: 认证补充表
-- ================================

CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '角色名称',
    code VARCHAR(64) NOT NULL COMMENT '角色编码',
    description VARCHAR(256) DEFAULT NULL COMMENT '角色描述',
    is_system TINYINT DEFAULT 0 COMMENT '是否系统预置',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
    UNIQUE KEY uk_name (name),
    UNIQUE KEY uk_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sys_menu (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    parent_id BIGINT UNSIGNED DEFAULT 0 COMMENT '父菜单ID',
    name VARCHAR(64) NOT NULL COMMENT '菜单名称',
    type TINYINT NOT NULL COMMENT '1=目录 2=菜单 3=按钮',
    path VARCHAR(256) DEFAULT NULL COMMENT '路由路径',
    component VARCHAR(256) DEFAULT NULL COMMENT '前端组件路径',
    permission_code VARCHAR(128) DEFAULT NULL COMMENT '权限标识',
    icon VARCHAR(64) DEFAULT NULL COMMENT '图标',
    sort_order INT DEFAULT 0 COMMENT '排序号',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_role_rel (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    role_id BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS role_menu_rel (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    role_id BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
    menu_id BIGINT UNSIGNED NOT NULL COMMENT '菜单ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_role_menu (role_id, menu_id),
    INDEX idx_role_id (role_id),
    INDEX idx_menu_id (menu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS login_history (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    ip_address VARCHAR(64) DEFAULT NULL COMMENT '登录IP',
    user_agent VARCHAR(512) DEFAULT NULL COMMENT '浏览器信息',
    login_result VARCHAR(16) NOT NULL COMMENT 'success / failed',
    fail_reason VARCHAR(128) DEFAULT NULL COMMENT '失败原因',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS password_reset_token (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    token VARCHAR(128) NOT NULL COMMENT '重置令牌',
    is_used TINYINT DEFAULT 0 COMMENT '是否已使用',
    expire_at DATETIME NOT NULL COMMENT '过期时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_token (token),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================
-- 成员B: 补充表
-- ================================

CREATE TABLE IF NOT EXISTS skill_param (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    skill_id BIGINT UNSIGNED NOT NULL COMMENT '关联技能ID',
    param_name VARCHAR(64) NOT NULL COMMENT '参数名',
    param_type VARCHAR(32) NOT NULL COMMENT 'string/number/boolean/object/array',
    is_required TINYINT DEFAULT 1 COMMENT '是否必填',
    description VARCHAR(256) DEFAULT NULL COMMENT '参数说明',
    default_value VARCHAR(256) DEFAULT NULL COMMENT '默认值',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_skill_id (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS employee_skill_rel (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT UNSIGNED NOT NULL COMMENT '数字员工ID',
    skill_id BIGINT UNSIGNED NOT NULL COMMENT '技能ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_emp_skill (employee_id, skill_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_skill_id (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS digital_employee_conversation (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT UNSIGNED NOT NULL COMMENT '数字员工ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '对话用户ID',
    user_message TEXT NOT NULL COMMENT '用户消息',
    bot_response TEXT NOT NULL COMMENT '机器人回复',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================
-- 成员C: 补充表
-- ================================

CREATE TABLE IF NOT EXISTS im_group_member (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    group_id BIGINT UNSIGNED NOT NULL COMMENT '群ID',
    user_type VARCHAR(16) NOT NULL COMMENT 'user / bot',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户/数字员工ID',
    role VARCHAR(16) DEFAULT 'member' COMMENT 'owner/admin/member',
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    UNIQUE KEY uk_group_member (group_id, user_type, user_id),
    INDEX idx_group_id (group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS im_contact (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    contact_user_id BIGINT UNSIGNED NOT NULL COMMENT '联系人用户ID',
    alias VARCHAR(64) DEFAULT NULL COMMENT '备注名',
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_contact (user_id, contact_user_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notification (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(32) NOT NULL COMMENT 'system/announcement/task/approval',
    title VARCHAR(256) NOT NULL COMMENT '通知标题',
    content TEXT NOT NULL COMMENT '通知内容',
    link VARCHAR(512) DEFAULT NULL COMMENT '跳转链接',
    sender_id BIGINT UNSIGNED DEFAULT NULL COMMENT '发送者ID',
    is_global TINYINT DEFAULT 0 COMMENT '是否全平台发送',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notification_read (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    notification_id BIGINT UNSIGNED NOT NULL COMMENT '通知ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    read_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '已读时间',
    UNIQUE KEY uk_notification_user (notification_id, user_id),
    INDEX idx_notification_id (notification_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================
-- 成员D: 补充表
-- ================================

CREATE TABLE IF NOT EXISTS sys_audit_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED DEFAULT NULL COMMENT '操作人ID',
    username VARCHAR(64) DEFAULT NULL COMMENT '操作人用户名',
    action VARCHAR(64) NOT NULL COMMENT '操作类型',
    resource VARCHAR(64) NOT NULL COMMENT '资源类型',
    resource_id BIGINT UNSIGNED DEFAULT NULL COMMENT '资源ID',
    detail JSON DEFAULT NULL COMMENT '操作详情',
    ip_address VARCHAR(64) DEFAULT NULL COMMENT '操作IP',
    user_agent VARCHAR(512) DEFAULT NULL COMMENT 'User Agent',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id_created (user_id, created_at),
    INDEX idx_action (action),
    INDEX idx_resource (resource)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================
-- 成员E: 补充表
-- ================================

CREATE TABLE IF NOT EXISTS nl2sql_favorite (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    query_history_id BIGINT UNSIGNED DEFAULT NULL COMMENT '关联的查询记录',
    question TEXT NOT NULL COMMENT '问题',
    sql TEXT NOT NULL COMMENT 'SQL',
    chart_type VARCHAR(32) DEFAULT NULL COMMENT '图表类型',
    note VARCHAR(256) DEFAULT NULL COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_query_history_id (query_history_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================
-- 成员F: 补充表
-- ================================

CREATE TABLE IF NOT EXISTS crawler_execution_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    task_id BIGINT UNSIGNED NOT NULL COMMENT '任务ID',
    status VARCHAR(16) NOT NULL COMMENT 'success/failed/running',
    rows_collected INT UNSIGNED DEFAULT 0 COMMENT '采集行数',
    rows_inserted INT UNSIGNED DEFAULT 0 COMMENT '入库行数',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    started_at DATETIME NOT NULL COMMENT '开始时间',
    finished_at DATETIME DEFAULT NULL COMMENT '结束时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS data_clean_rule (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '规则名称',
    rule_type VARCHAR(32) NOT NULL COMMENT 'dedup/normalize/mask/custom',
    config JSON NOT NULL COMMENT '规则配置',
    target_field VARCHAR(64) DEFAULT NULL COMMENT '目标字段',
    sort_order INT DEFAULT 0 COMMENT '执行顺序',
    task_id BIGINT UNSIGNED NOT NULL COMMENT '关联爬虫任务',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
    INDEX idx_task_id (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS file_record (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    original_name VARCHAR(256) NOT NULL COMMENT '原始文件名',
    stored_name VARCHAR(256) NOT NULL COMMENT '存储文件名',
    file_path VARCHAR(1024) NOT NULL COMMENT '存储路径',
    file_size BIGINT UNSIGNED NOT NULL COMMENT '文件大小(字节)',
    file_type VARCHAR(64) DEFAULT NULL COMMENT 'MIME类型',
    category VARCHAR(32) DEFAULT NULL COMMENT 'image/document/code/other',
    md5 VARCHAR(64) DEFAULT NULL COMMENT '文件MD5(去重)',
    upload_by BIGINT UNSIGNED NOT NULL COMMENT '上传者ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
    INDEX idx_upload_by (upload_by),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS file_share (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT UNSIGNED NOT NULL COMMENT '文件ID',
    share_code VARCHAR(64) NOT NULL COMMENT '分享码',
    password VARCHAR(128) DEFAULT NULL COMMENT '提取密码',
    expire_at DATETIME DEFAULT NULL COMMENT '过期时间',
    download_count INT UNSIGNED DEFAULT 0 COMMENT '下载次数',
    created_by BIGINT UNSIGNED NOT NULL COMMENT '分享者ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_share_code (share_code),
    INDEX idx_file_id (file_id),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sys_config (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(128) NOT NULL COMMENT '配置键',
    config_val