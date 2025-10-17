/**
 * AI图片生成相关类型定义
 */

export interface GenerateTextToImageRequest {
  prompt: string;
  model?: string;
  size?: string;
  quality?: string;
  n?: number;
}

export interface GenerateImageToImageRequest {
  prompt: string;
  model?: string;
  images?: File[];  // 新增：支持多图
  image?: File;     // 保留：向后兼容
  size?: string;
  n?: number;
}

export interface GeneratedImage {
  url: string;
  thumbnailUrl?: string;  // 缩略图URL（base64，前端生成）
  revised_prompt?: string;
}

export interface GenerateResponse {
  success: boolean;
  images?: GeneratedImage[];
  creations?: import('./gallery').Creation[];
  generation_time?: number;
  model_used?: string;
  prompt?: string;
  remaining_credits?: number;
  error?: string;
}

export interface AvailableModelsResponse {
  success: boolean;
  models: string[];
  sizes: string[];
}