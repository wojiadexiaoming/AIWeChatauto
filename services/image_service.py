"""
图像服务模块
处理图像生成和处理相关操作
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class ImageService:
    """图像服务类"""
    
    def __init__(self):
        self.client = None
        self.image_model = AppConfig.GEMINI_IMAGE_MODEL
        self.cache_folder = AppConfig.CACHE_FOLDER
        logger.info("图像服务初始化完成")
    
    def _get_client(self) -> genai.Client:
        """获取Gemini客户端"""
        if not self.client:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("未设置GEMINI_API_KEY环境变量")
            
            self.client = genai.Client(api_key=api_key)
            logger.info("Gemini客户端创建成功")
        
        return self.client
    
    def generate_article_image(self, title: str, description: str = "") -> Optional[str]:
        """
        生成文章配图
        :param title: 文章标题
        :param description: 文章描述
        :return: 图片文件路径
        """
        try:
            client = self._get_client()
            
            # 生成图片提示词
            image_prompt = self._build_image_prompt(title, description)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_{timestamp}.jpg"
            image_path = os.path.join(self.cache_folder, filename)
            
            logger.info(f"开始生成文章配图，标题: {title}")
            logger.debug(f"图片保存路径: {image_path}")
            
            response = client.models.generate_content(
                model=self.image_model,
                contents=image_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            if not response.candidates:
                logger.error("图片生成失败，无候选结果")
                return None
            
            content = response.candidates[0].content
            if not content or not content.parts:
                logger.error("图片生成失败，无内容部分")
                return None
            
            # 查找并保存图片数据
            image_saved = False
            for part in content.parts:
                if part.text:
                    logger.info(f"图片生成描述: {part.text}")
                elif part.inline_data and part.inline_data.data:
                    with open(image_path, 'wb') as f:
                        f.write(part.inline_data.data)
                    logger.info(f"文章配图生成成功: {image_path}")
                    image_saved = True
                    break
            
            if image_saved:
                return image_path
            else:
                logger.error("图片生成失败，未找到图片数据")
                return None
            
        except Exception as e:
            logger.error(f"生成文章配图时发生错误: {str(e)}")
            return None
    
    def _build_image_prompt(self, title: str, description: str = "") -> str:
        """
        构建图像生成提示词
        :param title: 文章标题
        :param description: 文章描述
        :return: 图像提示词
        """
        base_prompt = f"""
为文章《{title}》生成一张高质量的配图。

要求：
1. 图片风格现代、简洁、专业
2. 色调温和，适合微信公众号
3. 构图美观，有设计感
4. 与文章主题相关
5. 避免包含文字
6. 尺寸比例适合作为文章封面
7. 使用中国读者喜欢的视觉元素
"""
        
        if description:
            base_prompt += f"\n\n文章描述：{description}\n请根据文章内容生成相关的视觉元素。"
        
        return base_prompt
    
    def validate_image_file(self, image_path: str) -> bool:
        """
        验证图片文件
        :param image_path: 图片路径
        :return: 验证结果
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return False
            
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                logger.error(f"图片文件为空: {image_path}")
                return False
            
            # 检查文件大小（微信限制10MB）
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                logger.error(f"图片文件过大: {file_size} bytes, 最大限制: {max_size} bytes")
                return False
            
            logger.info(f"图片文件验证通过: {image_path}, 大小: {file_size} bytes")
            return True
            
        except Exception as e:
            logger.error(f"验证图片文件时发生错误: {str(e)}")
            return False
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        获取图片信息
        :param image_path: 图片路径
        :return: 图片信息
        """
        try:
            if not os.path.exists(image_path):
                return {'exists': False}
            
            file_size = os.path.getsize(image_path)
            file_name = os.path.basename(image_path)
            
            return {
                'exists': True,
                'file_name': file_name,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'full_path': image_path,
                'relative_path': os.path.relpath(image_path, '.'),
                'created_time': datetime.fromtimestamp(os.path.getctime(image_path)).strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"获取图片信息时发生错误: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def cleanup_old_images(self, days: int = 7) -> int:
        """
        清理旧图片文件
        :param days: 保留天数
        :return: 清理的文件数量
        """
        try:
            if not os.path.exists(self.cache_folder):
                return 0
            
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            cleaned_count = 0
            for filename in os.listdir(self.cache_folder):
                if filename.startswith('article_') and filename.endswith('.jpg'):
                    file_path = os.path.join(self.cache_folder, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"删除旧图片: {filename}")
            
            logger.info(f"清理完成，删除了 {cleaned_count} 个旧图片文件")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理旧图片时发生错误: {str(e)}")
            return 0
    
    def get_cache_folder_info(self) -> Dict[str, Any]:
        """
        获取缓存文件夹信息
        :return: 文件夹信息
        """
        try:
            if not os.path.exists(self.cache_folder):
                return {'exists': False}
            
            files = []
            total_size = 0
            
            for filename in os.listdir(self.cache_folder):
                file_path = os.path.join(self.cache_folder, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    files.append({
                        'name': filename,
                        'size': file_size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return {
                'exists': True,
                'file_count': len(files),
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files': files
            }
            
        except Exception as e:
            logger.error(f"获取缓存文件夹信息时发生错误: {str(e)}")
            return {'exists': False, 'error': str(e)}