/**
 * 画廊和作品相关类型定义
 */

export interface Creation {
  id: number;
  user_id: number;
  prompt: string;
  image_url: string;
  model_used: string;
  size: string;
  generation_time?: number;
  is_favorite: boolean;
  tags: string;
  category: string;
  visibility: string;
  created_at: string;
  updated_at: string;
}

export interface GalleryStats {
  total: number;
  favorites: number;
  recent_week: number;
  categories: { category: string; count: number }[];
}

export interface GalleryResponse {
  success: boolean;
  creations: Creation[];
  page: number;
  per_page: number;
  stats: GalleryStats;
  error?: string;
}

export interface GalleryFilters {
  page?: number;
  per_page?: number;
  category?: string;
  tags?: string;
  search?: string;
  is_favorite?: boolean;
}