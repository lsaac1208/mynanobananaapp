/**
 * 作品相关类型定义
 */

export interface Creation {
  id: number;
  user_id: number;
  prompt: string;
  image_url: string;
  model_used: string;
  size: string;
  created_at: string;
}

export interface CreateTextToImageRequest {
  prompt: string;
  model: 'nano-banana' | 'nano-banana-hd';
  size: '1:1' | '16:9' | '9:16' | '4:3' | '3:4';
}

export interface CreateImageToImageRequest {
  prompt: string;
  model: 'nano-banana' | 'nano-banana-hd';
  size: '1:1' | '16:9' | '9:16' | '4:3' | '3:4';
  images: File[];
}

export interface GenerateResponse {
  message: string;
  creation: Creation;
  remaining_credits: number;
}

export interface GalleryResponse {
  creations: Creation[];
  total: number;
  page: number;
  per_page: number;
}