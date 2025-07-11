"""
Gemini AI服务模块
处理Google Gemini AI相关操作
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini AI服务类"""
    
    def __init__(self):
        self.client = None
        self.default_model = AppConfig.GEMINI_DEFAULT_MODEL
        self.image_model = AppConfig.GEMINI_IMAGE_MODEL
        logger.info("Gemini服务初始化完成")
    
    def _get_client(self) -> genai.Client:
        """获取Gemini客户端"""
        if not self.client:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("未设置GEMINI_API_KEY环境变量")
            
            self.client = genai.Client(api_key=api_key)
            logger.info("Gemini客户端创建成功")
        
        return self.client
    
    def generate_content(self, prompt: str, model: str = None) -> Optional[str]:
        """
        生成内容
        :param prompt: 提示词
        :param model: 模型名称
        :return: 生成的内容
        """
        if not model:
            model = self.default_model
            
        try:
            client = self._get_client()
            logger.info(f"开始生成内容，使用模型: {model}")
            logger.debug(f"提示词长度: {len(prompt)} 字符")
            
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            
            if response and response.text:
                content = response.text.strip()
                logger.info(f"内容生成成功，长度: {len(content)} 字符")
                return content
            else:
                logger.error("内容生成失败，响应为空")
                return None
                
        except Exception as e:
            logger.error(f"生成内容时发生错误: {str(e)}")
            return None
    
    def generate_article_content(self, title: str, model: str = None) -> Optional[str]:
        """
        生成文章内容
        :param title: 文章标题
        :param model: 模型名称
        :return: 文章内容（HTML格式）
        """
        logger.info(f"开始生成文章内容，标题: {title}")
        
        prompt = self._build_article_prompt(title)
        content = self.generate_content(prompt, model)
        
        if content:
            logger.info("文章内容生成成功")
            return content
        else:
            logger.error("文章内容生成失败")
            return None
    
    def _build_article_prompt(self, title: str) -> str:
        """构建文章生成提示词"""
        return f"""
请为以下标题创作一篇高质量的微信公众号文章：

标题：{title}

要求：
1. 文章长度适中，约1000-1500字
2. 内容要有深度和价值，不要空洞无物
3. 结构清晰，包含引言、正文和结论
4. 使用HTML格式，包含适当的标题标签（h2, h3）和段落标签（p）
5. 语言生动有趣，适合微信公众号读者
6. 内容要原创，有独特见解
7. 适当使用项目符号或编号列表来增强可读性
8. 避免使用过于专业的术语，保持通俗易懂

请直接输出HTML格式的文章内容，不要包含任何其他说明文字：
"""
    
    def generate_digest(self, title: str, content: str, model: str = None) -> str:
        """
        生成文章摘要
        :param title: 文章标题
        :param content: 文章内容
        :param model: 模型名称
        :return: 文章摘要
        """
        logger.info(f"开始生成文章摘要，标题: {title}")
        
        # 截取内容前800字符用于生成摘要
        content_preview = self._clean_html_content(content[:800]) if content else ""
        
        prompt = self._build_digest_prompt(title, content_preview)
        digest = self.generate_content(prompt, model)
        
        if digest:
            # 限制摘要长度
            if len(digest) > 120:
                digest = digest[:100] + "..."
            logger.info(f"文章摘要生成成功: {digest}")
            return digest
        else:
            default_digest = f"探索{title}的深度解析，获取独特见解和实用价值。"
            logger.warning(f"摘要生成失败，使用默认摘要: {default_digest}")
            return default_digest
    
    def _build_digest_prompt(self, title: str, content_preview: str) -> str:
        """构建摘要生成提示词"""
        return f"""
请为以下文章生成一个简洁的摘要：

标题：{title}
内容预览：{content_preview}

要求：
1. 摘要长度不超过100字
2. 概括文章的核心内容和价值
3. 语言吸引人，能激发读者的阅读兴趣
4. 不要包含HTML标签，纯文本即可
5. 使用中文表达

请直接输出摘要内容，不要包含任何其他说明文字：
"""
    
    def _clean_html_content(self, html_content: str) -> str:
        """清理HTML内容，提取纯文本"""
        import re
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        # 移除多余空白
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    
    def test_connection(self, model: str = None) -> Dict[str, Any]:
        """
        测试Gemini AI连接
        :param model: 模型名称
        :return: 测试结果
        """
        logger.info("开始测试Gemini AI连接")
        
        try:
            test_content = self.generate_content("请说'测试成功'", model)
            
            if test_content and "测试成功" in test_content:
                logger.info("Gemini AI连接测试成功")
                return {
                    'success': True,
                    'message': 'Gemini AI连接成功',
                    'data': {
                        'response': test_content,
                        'model': model or self.default_model
                    }
                }
            else:
                logger.error("Gemini AI连接测试失败")
                return {
                    'success': False,
                    'message': 'Gemini AI连接失败，请检查API密钥'
                }
                
        except Exception as e:
            logger.error(f"测试Gemini AI连接时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'Gemini AI连接测试失败: {str(e)}'
            }
    
    def set_api_key(self, api_key: str):
        """
        设置API密钥
        :param api_key: API密钥
        """
        os.environ["GEMINI_API_KEY"] = api_key
        # 重置客户端，强制使用新密钥
        self.client = None
        logger.info("Gemini API密钥已更新")
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        return [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash-preview-image-generation"
        ]