"""
文章控制器模块
处理文章生成和发布相关的HTTP请求
"""

import logging
from flask import request, jsonify
from typing import Dict, Any
from services.config_service import ConfigService
from services.gemini_service import GeminiService
from services.image_service import ImageService
from services.wechat_service import WeChatService
from services.draft_service import DraftService

logger = logging.getLogger(__name__)

class ArticleController:
    """文章控制器类"""
    
    def __init__(self):
        self.config_service = ConfigService()
        self.gemini_service = GeminiService()
        self.image_service = ImageService()
        self.wechat_service = WeChatService()
        self.draft_service = DraftService()
        logger.info("文章控制器初始化完成")
    
    def generate_article(self) -> Dict[str, Any]:
        """
        生成文章
        :return: 响应数据
        """
        try:
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            title = data.get('title', '').strip()
            if not title:
                return {
                    'success': False,
                    'message': '请输入文章标题'
                }
            
            logger.info(f"开始生成文章，标题: {title}")
            
            # 检查Gemini配置
            gemini_config = self.config_service.get_gemini_config()
            if not gemini_config['api_key']:
                return {
                    'success': False,
                    'message': '请先配置Gemini API密钥'
                }
            
            # 设置API密钥
            self.gemini_service.set_api_key(gemini_config['api_key'])
            
            # 生成文章内容
            logger.info("开始生成文章内容")
            content = self.gemini_service.generate_article_content(title, gemini_config['model'])
            if not content:
                return {
                    'success': False,
                    'message': '文章内容生成失败'
                }
            
            # 生成文章摘要
            logger.info("开始生成文章摘要")
            digest = self.gemini_service.generate_digest(title, content, gemini_config['model'])
            
            # 生成配图
            image_url = None
            try:
                logger.info("开始生成文章配图")
                image_path = self.image_service.generate_article_image(title, digest)
                if image_path:
                    image_url = f"/cache/{os.path.basename(image_path)}"
                    logger.info(f"配图生成成功: {image_path}")
            except Exception as e:
                logger.warning(f"配图生成失败: {str(e)}")
            
            # 构建响应数据
            import os
            from datetime import datetime
            response_data = {
                'title': title,
                'content': content,
                'digest': digest,
                'image_url': image_url,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content_length': len(content),
                'has_image': bool(image_url)
            }
            
            logger.info("文章生成完成")
            return {
                'success': True,
                'message': '文章生成成功',
                'data': response_data
            }
            
        except Exception as e:
            logger.error(f"生成文章时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'生成文章失败: {str(e)}'
            }
    
    def publish_article(self) -> Dict[str, Any]:
        """
        发布文章到微信公众号
        :return: 响应数据
        """
        try:
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            article_data = data.get('article')
            if not article_data:
                return {
                    'success': False,
                    'message': '缺少文章数据'
                }
            
            logger.info(f"开始发布文章: {article_data.get('title', 'Unknown')}")
            
            # 检查微信配置
            wechat_config = self.config_service.get_wechat_config()
            if not wechat_config['appid'] or not wechat_config['appsecret']:
                return {
                    'success': False,
                    'message': '请先配置微信公众号信息'
                }
            
            # 获取access_token
            logger.info("获取微信access_token")
            token_info = self.wechat_service.get_access_token(
                wechat_config['appid'],
                wechat_config['appsecret']
            )
            
            if not token_info or not token_info.get('access_token'):
                return {
                    'success': False,
                    'message': '获取微信access_token失败'
                }
            
            access_token = token_info['access_token']
            
            # 上传配图（如果有）
            thumb_media_id = None
            if article_data.get('image_url'):
                logger.info("开始上传文章配图")
                image_path = self._get_image_path(article_data['image_url'])
                if image_path and self.image_service.validate_image_file(image_path):
                    upload_result = self.wechat_service.upload_permanent_material(
                        access_token, image_path, 'image'
                    )
                    if upload_result and upload_result.get('media_id'):
                        thumb_media_id = upload_result['media_id']
                        logger.info(f"配图上传成功，media_id: {thumb_media_id}")
                    else:
                        logger.warning("配图上传失败")
            
            # 获取作者配置
            author_config = self.config_service.get_author_config()
            
            # 创建草稿
            logger.info("开始创建草稿")
            draft_data = self.draft_service.build_draft_data(
                title=article_data['title'],
                content=article_data['content'],
                author=author_config['author'],
                digest=article_data.get('digest', ''),
                thumb_media_id=thumb_media_id or '',
                content_source_url=author_config['content_source_url']
            )
            
            # 验证草稿数据
            if not self.draft_service.validate_draft_data(draft_data):
                return {
                    'success': False,
                    'message': '草稿数据验证失败'
                }
            
            # 创建草稿
            draft_result = self.draft_service.create_draft(access_token, draft_data)
            if not draft_result or not draft_result.get('media_id'):
                return {
                    'success': False,
                    'message': '创建草稿失败'
                }
            
            media_id = draft_result['media_id']
            logger.info(f"草稿创建成功，media_id: {media_id}")
            
            # 发布草稿
            logger.info("开始发布草稿")
            publish_result = self.draft_service.publish_draft(access_token, media_id)
            
            if publish_result and publish_result.get('errcode') == 0:
                logger.info("文章发布成功")
                return {
                    'success': True,
                    'message': '文章发布成功',
                    'data': {
                        'publish_id': publish_result.get('publish_id'),
                        'msg_data_id': publish_result.get('msg_data_id'),
                        'media_id': media_id,
                        'draft_info': self.draft_service.get_draft_info(draft_data)
                    }
                }
            else:
                error_msg = publish_result.get('errmsg', '发布失败') if publish_result else '发布失败'
                logger.error(f"文章发布失败: {error_msg}")
                return {
                    'success': False,
                    'message': f'文章发布失败: {error_msg}'
                }
                
        except Exception as e:
            logger.error(f"发布文章时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'发布文章失败: {str(e)}'
            }
    
    def _get_image_path(self, image_url: str) -> str:
        """
        从图片URL获取本地路径
        :param image_url: 图片URL
        :return: 本地路径
        """
        if image_url.startswith('/cache/'):
            return image_url.replace('/cache/', 'cache/')
        return image_url
    
    def get_article_preview(self) -> Dict[str, Any]:
        """
        获取文章预览
        :return: 响应数据
        """
        try:
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            # 这里可以添加预览逻辑
            # 例如：格式化内容、处理图片等
            
            return {
                'success': True,
                'message': '预览数据获取成功',
                'data': data
            }
            
        except Exception as e:
            logger.error(f"获取文章预览时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'获取预览失败: {str(e)}'
            }