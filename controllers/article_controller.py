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
        实现完整的文章生成逻辑：
        1. 根据标题联网搜索或AI理解生成内容
        2. 根据文章长度生成合适数量的配图
        3. 记录配图插入位置
        4. 生成配图并插入图片URL
        :return: 响应数据
        """
        try:
            data = request.get_json()
            logger.info(f"收到文章生成请求: {data}")
            
            if not data:
                logger.error("请求数据为空")
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            title = data.get('title', '').strip()
            if not title:
                logger.error("文章标题为空")
                return {
                    'success': False,
                    'message': '请输入文章标题'
                }
            
            logger.info(f"开始生成文章，标题: {title}")
            
            # 检查Gemini配置
            gemini_config = self.config_service.get_gemini_config()
            logger.info(f"Gemini配置检查: api_key={'已设置' if gemini_config.get('api_key') else '未设置'}")
            
            if not gemini_config['api_key']:
                return {
                    'success': False,
                    'message': '请先配置Gemini API密钥'
                }
            
            # 设置API密钥
            self.gemini_service.set_api_key(gemini_config['api_key'])
            
            # 第一步：生成文章内容（包含搜索结果和AI理解）
            logger.info("第一步：开始生成文章内容")
            content = self.gemini_service.generate_article_content(title, gemini_config['model'])
            if not content:
                logger.error("文章内容生成失败")
                return {
                    'success': False,
                    'message': '文章内容生成失败'
                }
            
            logger.info(f"文章内容生成成功，长度: {len(content)}字符")
            
            # 第二步：生成文章摘要
            logger.info("第二步：开始生成文章摘要")
            digest = self.gemini_service.generate_digest(title, content, gemini_config['model'])
            logger.info(f"摘要生成完成: {digest[:50]}...")
            
            # 第三步：根据文章长度确定配图数量和位置
            logger.info("第三步：确定配图数量和插入位置")
            word_count = len(content.replace('<', '').replace('>', ''))  # 粗略计算字数
            image_count = max(1, min(3, word_count // 500))  # 每500字一张图，最少1张最多3张
            logger.info(f"文章字数约: {word_count}，计划生成配图数量: {image_count}")
            
            # 第四步：生成配图并插入
            logger.info("第四步：开始生成和插入配图")
            processed_content = self._process_images_in_content(content, title, digest, image_count)
            
            # 构建响应数据
            import os
            from datetime import datetime
            response_data = {
                'title': title,
                'content': processed_content,
                'digest': digest,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'content_length': len(processed_content),
                'image_count': image_count,
                'author': self.config_service.get_config_value('author', 'AI笔记'),
                'content_source_url': self.config_service.get_config_value('content_source_url', '')
            }
            
            logger.info("文章生成完成")
            logger.info(f"生成结果预览: 标题={title}, 内容长度={len(processed_content)}, 配图数量={image_count}")
            
            return {
                'success': True,
                'message': '文章生成成功',
                'data': response_data
            }
            
        except Exception as e:
            logger.error(f"生成文章时发生错误: {str(e)}", exc_info=True)
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
    
    def _process_images_in_content(self, content: str, title: str, description: str, image_count: int) -> str:
        """
        在文章内容中处理配图：生成图片并插入到合适位置
        :param content: 原始文章内容
        :param title: 文章标题
        :param description: 文章描述
        :param image_count: 配图数量
        :return: 插入配图后的内容
        """
        try:
            logger.info(f"开始处理文章配图，计划生成{image_count}张图片")
            
            # 将内容按段落分割
            paragraphs = content.split('</p>')
            total_paragraphs = len(paragraphs)
            
            if total_paragraphs < 2:
                logger.warning("文章段落过少，跳过配图插入")
                return content
            
            # 计算插入位置
            insert_positions = []
            if image_count == 1:
                insert_positions = [total_paragraphs // 2]
            elif image_count == 2:
                insert_positions = [total_paragraphs // 3, 2 * total_paragraphs // 3]
            elif image_count >= 3:
                insert_positions = [total_paragraphs // 4, total_paragraphs // 2, 3 * total_paragraphs // 4]
            
            logger.info(f"计划在第{insert_positions}段后插入配图")
            
            # 生成配图
            generated_images = []
            for i in range(min(image_count, len(insert_positions))):
                try:
                    logger.info(f"生成第{i+1}张配图")
                    # 根据文章内容生成更有针对性的图片提示
                    image_prompt = f"{title} - 配图{i+1}"
                    image_path = self.image_service.generate_article_image(image_prompt, description)
                    
                    if image_path:
                        # 这里应该是微信图片URL，暂时用占位符
                        # 在实际发布时需要先上传到微信获取正式URL
                        image_url = f"https://mmbiz.qpic.cn/placeholder_{i+1}.jpg"
                        generated_images.append({
                            'local_path': image_path,
                            'placeholder_url': image_url,
                            'position': insert_positions[i]
                        })
                        logger.info(f"第{i+1}张配图生成成功: {image_path}")
                    else:
                        logger.warning(f"第{i+1}张配图生成失败")
                        
                except Exception as e:
                    logger.error(f"生成第{i+1}张配图时出错: {str(e)}")
            
            # 从后往前插入图片，避免位置偏移
            processed_content = content
            for img_info in reversed(generated_images):
                position = img_info['position']
                image_html = f'<p style="text-align: center;"><img src="{img_info["placeholder_url"]}" alt="文章配图" style="max-width: 100%; height: auto;"></p>'
                
                # 在指定位置插入图片
                parts = processed_content.split('</p>')
                if position < len(parts):
                    parts.insert(position, image_html)
                    processed_content = '</p>'.join(parts)
                    logger.info(f"在第{position}段后插入配图")
            
            logger.info(f"配图处理完成，共插入{len(generated_images)}张图片")
            return processed_content
            
        except Exception as e:
            logger.error(f"处理配图时发生错误: {str(e)}")
            return content  # 出错时返回原始内容