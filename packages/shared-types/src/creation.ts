/**
 * 作品相关类型定义（已移至gallery.ts，此文件保留用于其他定义）
 */

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