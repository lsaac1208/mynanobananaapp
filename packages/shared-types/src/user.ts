/**
 * 用户相关类型定义
 */

/**
 * 角色接口
 */
export interface Role {
  id: number;
  name: string;
  display_name: string;
  description: string;
  is_system?: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * 权限接口
 */
export interface Permission {
  id?: number;
  name: string;
  resource: string;
  action: string;
  description?: string;
}

/**
 * 用户接口
 */
export interface User {
  id: number;
  email: string;
  credits: number;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
  roles?: Role[];
}

export interface UserCreateRequest {
  email: string;
  password: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface UserProfile {
  id: number;
  email: string;
  credits: number;
  total_creations: number;
  created_at: string;
  roles?: Role[];
}

/**
 * 用户权限响应接口
 */
export interface UserPermissionsResponse {
  roles: Role[];
  permissions: string[];
}

/**
 * 角色列表响应接口
 */
export interface RolesResponse {
  roles: Role[];
}