/**
 * 管理员相关类型定义
 */

export interface AddCreditsRequest {
  user_email: string;
  credits: number;
  reason?: string;
}

export interface AddCreditsResponse {
  message: string;
  user: {
    email: string;
    credits_before: number;
    credits_after: number;
  };
}

export interface AdminStats {
  total_users: number;
  total_creations: number;
  total_credits_consumed: number;
  active_users_today: number;
  creations_today: number;
}

export interface DeleteUserResponse {
  success: boolean;
  message: string;
  deleted_user: {
    id: number;
    email: string;
    deleted_at: string;
  };
  impact: {
    creations_orphaned: number;
    sessions_deleted: number;
    behaviors_deleted: number;
    preferences_deleted: number;
    recommendations_deleted: number;
    performance_metrics_deleted: number;
  };
}