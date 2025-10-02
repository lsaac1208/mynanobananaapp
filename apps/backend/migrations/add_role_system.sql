-- ================================================
-- 角色权限系统数据库迁移脚本
-- 创建时间: 2025-09-30
-- 描述: 添加企业级角色权限系统，支持RBAC
-- ================================================

-- 1. 创建角色表
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- 角色名称 (admin, user, editor等)
    display_name TEXT NOT NULL,          -- 显示名称 (中文)
    description TEXT,                     -- 角色描述
    is_system BOOLEAN NOT NULL DEFAULT 0, -- 是否系统内置角色（不可删除）
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建用户-角色关联表 (多对多)
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,                   -- 授予者ID
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users (id) ON DELETE SET NULL,
    UNIQUE (user_id, role_id)             -- 同一用户不能重复拥有同一角色
);

-- 3. 创建权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,            -- 权限标识 (user.create, user.edit等)
    resource TEXT NOT NULL,               -- 资源类型 (user, creation, config等)
    action TEXT NOT NULL,                 -- 操作类型 (create, read, update, delete)
    description TEXT,                     -- 权限描述
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. 创建角色-权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE,
    UNIQUE (role_id, permission_id)
);

-- 5. 插入系统内置角色
INSERT INTO roles (name, display_name, description, is_system) VALUES
    ('admin', '管理员', '系统管理员，拥有所有权限', 1),
    ('user', '普通用户', '标准用户，可以使用AI生成功能', 1);

-- 6. 插入基础权限
INSERT INTO permissions (name, resource, action, description) VALUES
    -- 用户管理权限
    ('user.view', 'user', 'read', '查看用户信息'),
    ('user.create', 'user', 'create', '创建用户'),
    ('user.edit', 'user', 'update', '编辑用户信息'),
    ('user.delete', 'user', 'delete', '删除用户'),
    ('user.manage_credits', 'user', 'update', '管理用户次数'),

    -- AI生成权限
    ('generation.create', 'generation', 'create', '创建AI生成任务'),
    ('generation.view', 'generation', 'read', '查看生成历史'),
    ('generation.delete', 'generation', 'delete', '删除生成作品'),

    -- 画廊权限
    ('gallery.view', 'gallery', 'read', '查看个人画廊'),
    ('gallery.manage', 'gallery', 'update', '管理画廊作品'),

    -- 配置管理权限
    ('config.view', 'config', 'read', '查看系统配置'),
    ('config.edit', 'config', 'update', '编辑系统配置'),

    -- 系统管理权限
    ('system.analytics', 'system', 'read', '查看系统分析数据'),
    ('system.settings', 'system', 'update', '修改系统设置');

-- 7. 分配权限给角色
-- 管理员角色拥有所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM roles WHERE name = 'admin'),
    id
FROM permissions;

-- 普通用户角色权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM roles WHERE name = 'user'),
    id
FROM permissions
WHERE name IN (
    'generation.create',
    'generation.view',
    'generation.delete',
    'gallery.view',
    'gallery.manage'
);

-- 8. 迁移现有用户数据
-- 为ID=1的用户分配管理员角色
INSERT INTO user_roles (user_id, role_id, granted_by)
SELECT
    1,
    id,
    NULL
FROM roles
WHERE name = 'admin';

-- 为其他所有用户分配普通用户角色
INSERT INTO user_roles (user_id, role_id, granted_by)
SELECT
    u.id,
    r.id,
    NULL
FROM users u
CROSS JOIN roles r
WHERE r.name = 'user'
  AND u.id != 1
  AND NOT EXISTS (
    SELECT 1 FROM user_roles ur
    WHERE ur.user_id = u.id AND ur.role_id = r.id
  );

-- 9. 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);

-- 10. 创建视图方便查询用户权限
CREATE VIEW IF NOT EXISTS user_permissions_view AS
SELECT
    u.id AS user_id,
    u.email,
    r.name AS role_name,
    r.display_name AS role_display_name,
    p.name AS permission_name,
    p.resource,
    p.action
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE u.is_active = 1;

-- 完成迁移
SELECT 'Role system migration completed successfully!' AS status;