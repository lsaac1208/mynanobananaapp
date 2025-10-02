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
  image: File;
  model?: string;
  size?: string;
  n?: number;
}

export interface GeneratedImage {
  url: string;
  revised_prompt?: string;
}

export interface GenerateResponse {
  success: boolean;
  images?: GeneratedImage[];
  creations?: import('./creation').Creation[];
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