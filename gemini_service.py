import os
import logging
from datetime import datetime
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini AI服务封装"""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """获取Gemini客户端"""
        if not self.client:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("未设置GEMINI_API_KEY环境变量")
            self.client = genai.Client(api_key=api_key)
        return self.client
    
    def generate_content(self, prompt, model="gemini-2.5-flash"):
        """
        生成内容
        :param prompt: 提示词
        :param model: 模型名称
        :return: 生成的内容
        """
        try:
            client = self._get_client()
            logger.info(f"使用模型 {model} 生成内容")
            logger.debug(f"提示词: {prompt}")
            
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            
            if response and response.text:
                logger.info("内容生成成功")
                return response.text.strip()
            else:
                logger.error("内容生成失败，响应为空")
                return None
                
        except Exception as e:
            logger.error(f"生成内容时发生错误: {str(e)}")
            return None
    
    def generate_article_content(self, title, model="gemini-2.5-flash"):
        """
        生成文章内容
        :param title: 文章标题
        :param model: 模型名称
        :return: 文章内容（HTML格式）
        """
        prompt = f"""
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

请直接输出HTML格式的文章内容：
"""
        
        return self.generate_content(prompt, model)
    
    def generate_digest(self, title, content, model="gemini-2.5-flash"):
        """
        生成文章摘要
        :param title: 文章标题
        :param content: 文章内容
        :param model: 模型名称
        :return: 文章摘要
        """
        # 截取内容前500字符用于生成摘要
        content_preview = content[:500] if content else ""
        
        prompt = f"""
请为以下文章生成一个简洁的摘要：

标题：{title}
内容预览：{content_preview}

要求：
1. 摘要长度不超过100字
2. 概括文章的核心内容和价值
3. 语言吸引人，能激发读者的阅读兴趣
4. 不要包含HTML标签，纯文本即可

请直接输出摘要内容：
"""
        
        digest = self.generate_content(prompt, model)
        if digest and len(digest) > 120:
            # 如果摘要太长，截取前100字符
            digest = digest[:100] + "..."
        
        return digest or f"探索{title}的深度解析，获取独特见解和实用价值。"
    
    def generate_article_image(self, title, model="gemini-2.0-flash-preview-image-generation"):
        """
        生成文章配图
        :param title: 文章标题
        :param model: 图像生成模型
        :return: 图片文件路径
        """
        try:
            client = self._get_client()
            
            # 生成图片提示词
            image_prompt = f"""
为文章《{title}》生成一张高质量的配图。

要求：
1. 图片风格现代、简洁、专业
2. 色调温和，适合微信公众号
3. 构图美观，有设计感
4. 与文章主题相关
5. 避免包含文字
6. 尺寸比例适合作为文章封面
"""
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_{timestamp}.jpg"
            image_path = os.path.join("cache", filename)
            
            logger.info(f"开始生成文章配图，保存路径: {image_path}")
            logger.debug(f"图片生成提示词: {image_prompt}")
            
            response = client.models.generate_content(
                model=model,
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
            
            # 查找图片数据
            for part in content.parts:
                if part.text:
                    logger.info(f"图片生成描述: {part.text}")
                elif part.inline_data and part.inline_data.data:
                    with open(image_path, 'wb') as f:
                        f.write(part.inline_data.data)
                    logger.info(f"文章配图生成成功，保存为: {image_path}")
                    return image_path
            
            logger.error("图片生成失败，未找到图片数据")
            return None
            
        except Exception as e:
            logger.error(f"生成文章配图时发生错误: {str(e)}")
            return None
