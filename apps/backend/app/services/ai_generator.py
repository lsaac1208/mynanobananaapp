"""
AI图片生成服务
使用nano-banana API进行图片生成
集成性能监控与用户行为分析 (Phase 1)
"""
import os
import asyncio
import aiohttp
import time
import json
import psutil
from typing import Dict, Any, Optional, List
from flask import current_app


class AIGeneratorService:
    """AI图片生成服务类"""

    def __init__(self):
        self.timeout = 180  # 增加到3分钟超时，适应AI生成时间
        self.max_retries = 2  # 最大重试次数
        self.retry_delay = 5  # 重试间隔（秒）

        # 从数据库动态加载配置
        self._load_config()

    def _load_config(self):
        """从数据库加载配置（支持热更新，使用新的API配置系统）"""
        from app.repositories.api_config_repository import APIConfigRepository
        from app.services.encryption_service import encryption_service

        try:
            # 使用新的APIConfigRepository获取激活配置
            config_repo = APIConfigRepository()
            active_config = config_repo.get_active()

            if not active_config:
                current_app.logger.warning("No active API configuration found, using fallback")
                raise ValueError("No active API configuration")

            # 从激活配置中提取Base URL和解密的API Key
            self.base_url = active_config['openai_hk_base_url']
            encrypted_key = active_config['openai_hk_api_key_encrypted']
            self.api_key = encryption_service.decrypt(encrypted_key)

            current_app.logger.info(f"✅ Loaded API config: {active_config.get('name', 'Unknown')} (ID: {active_config['id']})")

            if not self.base_url or not self.api_key:
                raise ValueError("Incomplete API configuration")

        except Exception as e:
            current_app.logger.warning(f"Failed to load config from database: {str(e)}, using fallback")
            # 使用Flask配置作为后备
            self.base_url = current_app.config.get('OPENAI_HK_BASE_URL', 'https://api.openai-hk.com')
            self.api_key = current_app.config.get('OPENAI_HK_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_HK_API_KEY not configured")

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统性能指标"""
        try:
            # CPU和内存使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_mb = memory.used // (1024 * 1024)

            # 计算服务器负载 (0-1)
            server_load = min(cpu_percent / 100.0, 1.0)

            return {
                'server_load': round(server_load, 3),
                'memory_usage_mb': memory_mb,
                'cpu_percent': round(cpu_percent, 1)
            }
        except Exception as e:
            current_app.logger.warning(f"Failed to get system metrics: {str(e)}")
            return {
                'server_load': 0.0,
                'memory_usage_mb': 0,
                'cpu_percent': 0.0
            }

    def _record_performance(self, user_id: int = None, operation_type: str = '',
                          model_used: str = None, prompt_length: int = None,
                          image_size: str = None, generation_time: float = None,
                          api_response_time: float = None, success: bool = True,
                          error_type: str = None, error_message: str = None):
        """记录性能指标到数据库"""
        try:
            from app.database import PerformanceMetric

            # 获取系统指标
            metrics = self._get_system_metrics()

            # 记录性能数据
            PerformanceMetric.record(
                user_id=user_id,
                operation_type=operation_type,
                model_used=model_used,
                prompt_length=prompt_length,
                image_size=image_size,
                generation_time=generation_time,
                api_response_time=api_response_time,
                success=success,
                error_type=error_type,
                error_message=error_message,
                server_load=metrics['server_load'],
                memory_usage_mb=metrics['memory_usage_mb']
            )

            current_app.logger.debug(f"Performance metrics recorded: {operation_type}, {generation_time}s")

        except Exception as e:
            current_app.logger.warning(f"Failed to record performance metrics: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头，确保API密钥安全"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'nano-banana-app/1.0'
        }

    async def _make_request_with_retry(self, session: aiohttp.ClientSession, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """带重试机制的请求方法"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                current_app.logger.info(f"尝试第 {attempt + 1} 次请求到 nano-banana API")
                current_app.logger.debug(f"Request URL: {url}")
                current_app.logger.debug(f"Request payload: {payload}")

                # 🔍 性能日志: 连接开始时间
                connect_start = time.time()
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with session.post(url, json=payload, headers=self._get_headers(), timeout=timeout) as response:
                    connect_time = time.time() - connect_start
                    current_app.logger.info(f"⏱️ 连接建立耗时: {connect_time:.2f}秒")
                    # 记录响应信息
                    current_app.logger.info(f"API 响应状态: {response.status}")
                    current_app.logger.info(f"API 响应Content-Type: {response.headers.get('Content-Type', 'unknown')}")

                    # 🔍 性能日志: 读取响应开始时间
                    read_start = time.time()
                    # 先读取原始响应文本
                    response_text = await response.text()
                    read_time = time.time() - read_start
                    current_app.logger.info(f"⏱️ 读取响应耗时: {read_time:.2f}秒 (响应大小: {len(response_text)} 字节)")
                    current_app.logger.debug(f"API 响应内容 (前500字符): {response_text[:500]}")

                    # 尝试解析JSON
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError as json_err:
                        current_app.logger.error(f"JSON解析失败: {str(json_err)}")
                        current_app.logger.error(f"响应不是有效的JSON，原始内容: {response_text[:1000]}")
                        raise ValueError(f"API返回的不是有效的JSON: {response_text[:200]}")

                    if response.status == 200:
                        current_app.logger.info(f"nano-banana API 请求成功 (尝试 {attempt + 1}/{self.max_retries + 1})")
                        return response_data
                    else:
                        error_msg = f"nano-banana API 错误: HTTP {response.status}"
                        if 'error' in response_data:
                            error_msg += f" - {response_data['error']}"
                        current_app.logger.warning(error_msg)
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_msg
                        )

            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
                last_exception = e
                current_app.logger.warning(f"尝试 {attempt + 1}/{self.max_retries + 1} 失败: {str(e)}")

                # 如果还有重试机会，等待后重试
                if attempt < self.max_retries:
                    current_app.logger.info(f"等待 {self.retry_delay} 秒后重试...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    current_app.logger.error(f"所有重试都失败，最后的错误: {str(e)}")

        # 所有重试都失败了
        if last_exception:
            raise last_exception
        else:
            raise Exception("未知错误：所有重试都失败")

    def _convert_ratio_to_pixels(self, ratio: str) -> str:
        """将比例格式转换为像素格式

        Args:
            ratio: 比例格式，如 '1x1', '16x9', '9x16' 等

        Returns:
            像素格式，如 '1024x1024', '1792x1024', '1024x1792' 等
        """
        # 比例到像素的映射表（基于1024像素）
        ratio_to_pixels = {
            '1x1': '1024x1024',      # 正方形
            '4x3': '1024x768',       # 传统照片
            '3x4': '768x1024',       # 竖版传统照片
            '16x9': '1792x1024',     # 宽屏
            '9x16': '1024x1792',     # 竖屏手机
            '2x3': '768x1152',       # 竖版
            '3x2': '1152x768',       # 横版
        }

        return ratio_to_pixels.get(ratio, '1024x1024')

    def _validate_text_to_image_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证文生图参数"""
        validated = {}

        # 必填参数
        if not params.get('prompt'):
            raise ValueError("Prompt is required")
        validated['prompt'] = str(params['prompt']).strip()

        if len(validated['prompt']) > 1000:
            raise ValueError("Prompt too long (max 1000 characters)")

        # 可选参数
        validated['model'] = params.get('model', 'nano-banana')
        if validated['model'] not in ['nano-banana', 'nano-banana-hd']:
            raise ValueError("Invalid model. Use 'nano-banana' or 'nano-banana-hd'")

        # 尺寸参数：接受比例格式，转换为像素格式
        size_ratio = params.get('size', '1x1')
        valid_sizes = ['1x1', '4x3', '3x4', '16x9', '9x16', '2x3', '3x2']
        if size_ratio not in valid_sizes:
            raise ValueError(f"Invalid size. Use one of: {valid_sizes}")

        # 转换为API要求的像素格式
        validated['size'] = self._convert_ratio_to_pixels(size_ratio)
        current_app.logger.debug(f"Size conversion: {size_ratio} -> {validated['size']}")

        validated['n'] = min(int(params.get('n', 1)), 4)  # 最多4张图片
        validated['quality'] = params.get('quality', 'standard')

        return validated

    def _validate_image_to_image_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证图生图参数"""
        validated = {}

        # 必填参数
        if not params.get('prompt'):
            raise ValueError("Prompt is required")
        validated['prompt'] = str(params['prompt']).strip()

        if not params.get('image'):
            raise ValueError("Image is required")
        validated['image'] = params['image']  # 应该是base64或文件对象

        # 可选参数
        validated['model'] = params.get('model', 'nano-banana')

        # 尺寸参数：接受比例格式，转换为像素格式
        size_ratio = params.get('size', '1x1')
        valid_sizes = ['1x1', '4x3', '3x4', '16x9', '9x16', '2x3', '3x2']
        if size_ratio not in valid_sizes:
            raise ValueError(f"Invalid size. Use one of: {valid_sizes}")

        # 转换为API要求的像素格式
        validated['size'] = self._convert_ratio_to_pixels(size_ratio)
        current_app.logger.debug(f"Size conversion (image-to-image): {size_ratio} -> {validated['size']}")

        validated['n'] = min(int(params.get('n', 1)), 4)

        return validated

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送异步HTTP请求，带重试机制"""
        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                return await self._make_request_with_retry(session, url, data)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            elif e.status == 401:
                raise Exception("Invalid API key")
            elif e.status == 400:
                raise Exception("Invalid request parameters")
            else:
                raise Exception(f"API request failed: {e.message}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            current_app.logger.error(f"nano-banana API 请求失败: {str(e)}")
            if "timeout" in str(e).lower():
                raise Exception("AI生成超时，请稍后重试。AI生成通常需要10-60秒时间。")
            else:
                raise Exception(f"网络请求失败: {str(e)}")

    async def _make_multipart_request_with_retry(self, session: aiohttp.ClientSession, url: str, form_data) -> Dict[str, Any]:
        """带重试机制的multipart请求方法"""
        last_exception = None
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'nano-banana-app/1.0'
            # 不设置Content-Type，让aiohttp自动处理
        }

        for attempt in range(self.max_retries + 1):
            try:
                current_app.logger.info(f"尝试第 {attempt + 1} 次图生图请求到 nano-banana API")

                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with session.post(url, data=form_data, headers=headers, timeout=timeout) as response:
                    response_data = await response.json()

                    if response.status == 200:
                        current_app.logger.info(f"图生图 API 请求成功 (尝试 {attempt + 1}/{self.max_retries + 1})")
                        return response_data
                    else:
                        error_msg = f"nano-banana API 错误: HTTP {response.status}"
                        if 'error' in response_data:
                            error_msg += f" - {response_data['error']}"
                        current_app.logger.warning(error_msg)
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_msg
                        )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                current_app.logger.warning(f"图生图尝试 {attempt + 1}/{self.max_retries + 1} 失败: {str(e)}")

                # 如果还有重试机会，等待后重试
                if attempt < self.max_retries:
                    current_app.logger.info(f"等待 {self.retry_delay} 秒后重试图生图...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    current_app.logger.error(f"图生图所有重试都失败，最后的错误: {str(e)}")

        # 所有重试都失败了
        if last_exception:
            raise last_exception
        else:
            raise Exception("未知错误：图生图所有重试都失败")

    async def _make_multipart_request(self, endpoint: str, form_data) -> Dict[str, Any]:
        """发送异步multipart HTTP请求，带重试机制"""
        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                return await self._make_multipart_request_with_retry(session, url, form_data)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            elif e.status == 401:
                raise Exception("Invalid API key")
            elif e.status == 400:
                raise Exception("Invalid request parameters")
            else:
                raise Exception(f"API request failed: {e.message}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            current_app.logger.error(f"图生图 API 请求失败: {str(e)}")
            if "timeout" in str(e).lower():
                raise Exception("图生图超时，请稍后重试。AI图片处理通常需要更长时间。")
            else:
                raise Exception(f"网络请求失败: {str(e)}")

    async def generate_text_to_image(self, params: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
        """文生图功能 - 集成性能监控"""
        # 🔍 性能日志: 总体开始时间
        total_start_time = time.time()
        current_app.logger.info(f"🚀 开始文生图生成 - 用户ID: {user_id}, 模型: {params.get('model', 'nano-banana')}")

        # 热更新配置（每次生成前从数据库重新加载）
        config_start = time.time()
        self._load_config()
        config_time = time.time() - config_start
        current_app.logger.info(f"⏱️ 配置加载耗时: {config_time:.3f}秒")

        # 参数验证
        validate_start = time.time()
        validated_params = self._validate_text_to_image_params(params)
        validate_time = time.time() - validate_start
        current_app.logger.info(f"⏱️ 参数验证耗时: {validate_time:.3f}秒")

        # 性能监控变量
        start_time = time.time()
        api_start_time = None
        api_response_time = None
        operation_type = 'text_to_image'
        error_type = None
        error_message = None

        # 构建请求数据
        request_data = {
            'model': validated_params['model'],
            'prompt': validated_params['prompt'],
            'n': validated_params['n'],
            'size': validated_params['size'],
            'quality': validated_params['quality'],
            'response_format': 'url'
        }

        try:
            # 记录API调用开始时间
            current_app.logger.info(f"📡 开始调用nano-banana API - 端点: v1/images/generations")
            api_start_time = time.time()
            result = await self._make_request('v1/images/generations', request_data)
            api_response_time = time.time() - api_start_time
            current_app.logger.info(f"⏱️ API调用总耗时: {api_response_time:.2f}秒")

            generation_time = time.time() - start_time
            total_time = time.time() - total_start_time
            current_app.logger.info(f"✅ 文生图完成 - API耗时: {api_response_time:.2f}秒, 总耗时: {total_time:.2f}秒")

            # 处理响应
            if 'data' not in result:
                raise Exception("Invalid response format")

            images = []
            for item in result['data']:
                if 'url' in item:
                    images.append({
                        'url': item['url'],
                        'revised_prompt': item.get('revised_prompt'),
                    })

            # 记录成功的性能指标
            self._record_performance(
                user_id=user_id,
                operation_type=operation_type,
                model_used=validated_params['model'],
                prompt_length=len(validated_params['prompt']),
                image_size=validated_params['size'],
                generation_time=generation_time,
                api_response_time=api_response_time,
                success=True
            )

            return {
                'success': True,
                'images': images,
                'generation_time': round(generation_time, 2),
                'model_used': validated_params['model'],
                'prompt': validated_params['prompt']
            }

        except Exception as e:
            generation_time = time.time() - start_time

            # 分析错误类型
            if "timeout" in str(e).lower():
                error_type = "timeout"
            elif "api" in str(e).lower() or "http" in str(e).lower():
                error_type = "api_error"
            else:
                error_type = "unknown_error"

            error_message = str(e)[:500]  # 限制错误消息长度

            # 记录失败的性能指标
            self._record_performance(
                user_id=user_id,
                operation_type=operation_type,
                model_used=validated_params.get('model'),
                prompt_length=len(validated_params.get('prompt', '')),
                image_size=validated_params.get('size'),
                generation_time=generation_time,
                api_response_time=api_response_time,
                success=False,
                error_type=error_type,
                error_message=error_message
            )

            current_app.logger.error(f"Text-to-image generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'generation_time': round(generation_time, 2)
            }

    async def generate_image_to_image(self, params: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
        """图生图功能 - 集成性能监控"""
        # 热更新配置（每次生成前从数据库重新加载）
        self._load_config()

        # 参数验证
        validated_params = self._validate_image_to_image_params(params)

        # 性能监控变量
        start_time = time.time()
        api_start_time = None
        api_response_time = None
        operation_type = 'image_to_image'
        error_type = None
        error_message = None

        # 构建multipart请求数据
        form_data = aiohttp.FormData()
        form_data.add_field('prompt', validated_params['prompt'])
        form_data.add_field('n', str(validated_params['n']))
        form_data.add_field('size', validated_params['size'])
        form_data.add_field('response_format', 'url')

        # 添加图片文件
        image_file = validated_params['image']
        if hasattr(image_file, 'read'):
            # FileStorage对象，需要读取内容
            image_content = image_file.read()
            filename = getattr(image_file, 'filename', 'image.png')
            content_type = getattr(image_file, 'content_type', 'image/png')
            form_data.add_field('image', image_content, filename=filename, content_type=content_type)
        else:
            # 二进制数据
            form_data.add_field('image', image_file, filename='image.png', content_type='image/png')

        try:
            # 记录API调用开始时间
            api_start_time = time.time()
            result = await self._make_multipart_request('v1/images/edits', form_data)
            api_response_time = time.time() - api_start_time

            generation_time = time.time() - start_time

            # 处理响应
            if 'data' not in result:
                raise Exception("Invalid response format")

            images = []
            for item in result['data']:
                if 'url' in item:
                    images.append({
                        'url': item['url'],
                        'revised_prompt': item.get('revised_prompt'),
                    })

            # 记录成功的性能指标
            self._record_performance(
                user_id=user_id,
                operation_type=operation_type,
                model_used=validated_params['model'],
                prompt_length=len(validated_params['prompt']),
                image_size=validated_params['size'],
                generation_time=generation_time,
                api_response_time=api_response_time,
                success=True
            )

            return {
                'success': True,
                'images': images,
                'generation_time': round(generation_time, 2),
                'model_used': validated_params['model'],
                'prompt': validated_params['prompt']
            }

        except Exception as e:
            generation_time = time.time() - start_time

            # 分析错误类型
            if "timeout" in str(e).lower():
                error_type = "timeout"
            elif "api" in str(e).lower() or "http" in str(e).lower():
                error_type = "api_error"
            else:
                error_type = "unknown_error"

            error_message = str(e)[:500]  # 限制错误消息长度

            # 记录失败的性能指标
            self._record_performance(
                user_id=user_id,
                operation_type=operation_type,
                model_used=validated_params.get('model'),
                prompt_length=len(validated_params.get('prompt', '')),
                image_size=validated_params.get('size'),
                generation_time=generation_time,
                api_response_time=api_response_time,
                success=False,
                error_type=error_type,
                error_message=error_message
            )

            current_app.logger.error(f"Image-to-image generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'generation_time': round(generation_time, 2)
            }

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return ['nano-banana', 'nano-banana-hd']

    def get_available_sizes(self) -> List[str]:
        """获取可用尺寸列表"""
        return ['1x1', '4x3', '3x4', '16x9', '9x16', '2x3', '3x2']


# 单例实例
_ai_generator_service = None

def get_ai_generator_service() -> AIGeneratorService:
    """获取AI生成服务实例"""
    global _ai_generator_service
    if _ai_generator_service is None:
        _ai_generator_service = AIGeneratorService()
    return _ai_generator_service