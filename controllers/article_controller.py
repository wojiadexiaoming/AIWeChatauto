"""
文章控制器模块
处理文章生成和发布相关的HTTP请求
"""

import logging
from flask import request, jsonify
from typing import Dict, Any
from services.config_service import ConfigService
from services.gemini_service import GeminiService
from services.deepseek_service import DeepSeekService
from services.dashscope_service import DashScopeService
from services.image_service import ImageService
from services.wechat_service import WeChatService
from services.draft_service import DraftService
from services.history_service import HistoryService

logger = logging.getLogger(__name__)

class ArticleController:
    """文章控制器类"""
    
    def __init__(self):
        self.config_service = ConfigService()
        self.gemini_service = GeminiService()
        self.deepseek_service = DeepSeekService()
        self.dashscope_service = DashScopeService()
        self.image_service = ImageService()
        self.wechat_service = WeChatService()
        self.draft_service = DraftService()
        self.history_service = HistoryService()
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
        import uuid
        req_id = str(uuid.uuid4())
        logger.info(f"【唯一请求ID】{req_id} - generate_article")
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
            
            # 获取AI模型配置
            ai_model = data.get('ai_model', 'gemini')  # 默认使用Gemini
            image_model = data.get('image_model', 'gemini')  # 默认使用Gemini生图
            logger.info(f"使用AI模型: {ai_model}, 生图模型: {image_model}")
            
            # 根据选择的模型进行配置检查
            if ai_model == 'gemini':
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
                model_name = gemini_config.get('model', 'gemini-1.5-flash')
                
            elif ai_model == 'deepseek':
                # 检查DeepSeek配置
                deepseek_config = self.config_service.get_deepseek_config()
                logger.info(f"DeepSeek配置检查: api_key={'已设置' if deepseek_config.get('api_key') else '未设置'}")
                
                if not deepseek_config['api_key']:
                    return {
                        'success': False,
                        'message': '请先配置DeepSeek API密钥'
                    }
                
                # 设置API密钥
                self.deepseek_service.set_api_key(deepseek_config['api_key'])
                model_name = deepseek_config.get('model', 'deepseek-chat')
                
            elif ai_model == 'dashscope':
                # 检查阿里云百炼配置
                dashscope_config = self.config_service.get_dashscope_config()
                logger.info(f"阿里云百炼配置检查: api_key={'已设置' if dashscope_config.get('api_key') else '未设置'}")
                
                if not dashscope_config['api_key']:
                    return {
                        'success': False,
                        'message': '请先配置阿里云百炼API密钥'
                    }
                
                # 设置API密钥
                self.dashscope_service = DashScopeService(dashscope_config['api_key'])
                model_name = dashscope_config.get('model', 'qwen-turbo')
                
            else:
                return {
                    'success': False,
                    'message': f'不支持的AI模型: {ai_model}'
                }
            
            # 新增：接收前端传递的字数、配图数量和格式模板
            word_count = data.get('word_count')
            image_count = data.get('image_count')
            format_template = data.get('format_template', '')

            # 第一步：生成文章内容（包含搜索结果和AI理解）
            logger.info(f"第一步：开始生成文章内容，使用模型: {model_name}")
            
            if ai_model == 'gemini':
                content = self.gemini_service.generate_article_content(title, model_name, word_count, format_template=format_template)
            elif ai_model == 'deepseek':
                content = self.deepseek_service.generate_article_content(title, model_name, word_count, format_template=format_template)
            elif ai_model == 'dashscope':
                content = self.dashscope_service.generate_article_content(title, model_name, word_count, format_template=format_template)
            else:
                return {
                    'success': False,
                    'message': f'不支持的AI模型: {ai_model}'
                }
            
            if not content:
                logger.error("文章内容生成失败")
                return {
                    'success': False,
                    'message': '文章内容生成失败'
                }
            logger.info(f"文章内容生成成功，长度: {len(content)}字符")

            # 第二步：生成文章摘要
            logger.info("第二步：开始生成文章摘要")
            if ai_model == 'gemini':
                digest = self.gemini_service.generate_digest(title, content, model_name)
            elif ai_model == 'deepseek':
                digest = self.deepseek_service.generate_digest(title, content, model_name)
            elif ai_model == 'dashscope':
                digest = self.dashscope_service.generate_digest(title, content, model_name)
            else:
                digest = f"探索{title}的深度解析，获取独特见解和实用价值。"
            
            logger.info(f"摘要生成完成: {digest[:50]}...")

            # 第三步：根据参数或内容确定配图数量
            if not word_count:
                word_count = len(content.replace('<', '').replace('>', ''))
            if not image_count:
                image_count = max(1, min(3, int(word_count) // 500))
            else:
                image_count = int(image_count)
            logger.info(f"文章字数约: {word_count}，计划生成配图数量: {image_count}")

            # 第四步：生成配图并插入
            logger.info("第四步：开始生成和插入配图")
            custom_image_prompt = data.get('custom_image_prompt', '').strip()
            dashscope_image_model_code = data.get('dashscope_image_model_code', '').strip()
            if image_model == 'dashscope' and dashscope_image_model_code:
                image_model_code = dashscope_image_model_code
            else:
                image_model_code = image_model
            # 后续传递 image_model_code 给图片生成逻辑
            dashscope_params = data.get('dashscope_params', {})
            content_with_images = self._process_images_in_content(
                content, title, digest, image_count, image_model_code, ai_model, custom_image_prompt,
                dashscope_params=dashscope_params, dashscope_image_model_code=dashscope_image_model_code
            )
            
            # 第四点五步：输出原始文章内容到cache文件夹，便于对比
            try:
                import os
                from datetime import datetime
                safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cache_dir = 'cache'
                if not os.path.exists(cache_dir):
                    os.makedirs(cache_dir)
                raw_file_path = os.path.join(cache_dir, f"article_raw_{safe_title}_{timestamp}.html")
                with open(raw_file_path, 'w', encoding='utf-8') as f:
                    f.write(content_with_images)
                logger.info(f"原始文章内容已保存到: {raw_file_path}")
            except Exception as e:
                logger.error(f"保存原始文章内容到cache失败: {str(e)}")

            # 第五步：清理AI生成内容中的多余部分
            logger.info("第五步：开始清理内容中的多余部分")
            processed_content = self._clean_ai_generated_content(content_with_images)
            
            # 限制最终HTML内容不超过2万字符
            max_chars = 20000
            if len(processed_content) > max_chars:
                logger.warning(f"生成内容超出2万字符，已自动截断。原长度: {len(processed_content)}")
                processed_content = processed_content[:max_chars]
            
            # 第六步：保存删减后的文章到cache文件夹
            try:
                import os
                from datetime import datetime
                safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cache_dir = 'cache'
                if not os.path.exists(cache_dir):
                    os.makedirs(cache_dir)
                cleaned_file_path = os.path.join(cache_dir, f"article_cleaned_{safe_title}_{timestamp}.html")
                with open(cleaned_file_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                logger.info(f"删减后的文章内容已保存到: {cleaned_file_path}")
            except Exception as e:
                logger.error(f"保存删减后文章内容到cache失败: {str(e)}")
            
            # 记录带图内容摘要
            logger.info(f"[历史记录] 生成文章: 标题={title}, 内容前100字={processed_content[:100]}, 图片数={processed_content.count('<img')}")
            
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
            
            # 添加生成历史记录
            self.history_service.add_generation_history(response_data)
            
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
    
    def save_draft(self) -> Dict[str, Any]:
        """
        保存文章草稿到微信公众号
        :return: 响应数据
        """
        import uuid
        req_id = str(uuid.uuid4())
        logger.info(f"【唯一请求ID】{req_id} - save_draft")
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
            
            logger.info(f"开始保存草稿: {article_data.get('title', 'Unknown')}")
            
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
            
            # 处理文章内容中的图片，上传到微信平台并替换为微信URL，并收集media_id
            image_process_result = self._process_content_images(article_data['content'], access_token)
            processed_content = image_process_result['content']
            # 记录草稿内容摘要
            logger.info(f"[草稿保存] 标题={article_data.get('title', 'Unknown')}, 内容前100字={processed_content[:100]}, 图片数={processed_content.count('<img')}")
            images = image_process_result['images']
            thumb_media_id = images[0]['media_id'] if images and images[0].get('media_id') else ''
            
            # 获取作者配置
            author_config = self.config_service.get_author_config()
            
            # 创建草稿数据，使用第一个图片的media_id作为thumb_media_id
            logger.info("开始创建草稿")
            draft_data = self.draft_service.build_draft_data(
                title=article_data['title'],
                content=processed_content,
                author=author_config['author'],
                digest=article_data.get('digest', ''),
                thumb_media_id=thumb_media_id,
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
                error_msg = draft_result.get('errmsg', '创建草稿失败') if draft_result else '创建草稿失败'
                logger.error(f"创建草稿失败: {error_msg}")
                return {
                    'success': False,
                    'message': f'创建草稿失败: {error_msg}'
                }
            
            media_id = draft_result['media_id']
            logger.info(f"草稿保存成功，media_id: {media_id}")
            
            # 更新历史记录状态
            self.history_service.update_draft_status(article_data['title'], media_id)
            
            return {
                'success': True,
                'message': '草稿保存成功',
                'data': {
                    'media_id': media_id,
                    'draft_info': self.draft_service.get_draft_info(draft_data)
                }
            }
                
        except Exception as e:
            logger.error(f"保存草稿时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'保存草稿失败: {str(e)}'
            }
    
    def publish_draft(self) -> Dict[str, Any]:
        """
        发布草稿到微信公众号
        :return: 响应数据
        """
        import uuid
        req_id = str(uuid.uuid4())
        logger.info(f"【唯一请求ID】{req_id} - publish_draft")
        try:
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            media_id = data.get('media_id')
            if not media_id:
                return {
                    'success': False,
                    'message': '缺少草稿media_id'
                }
            
            logger.info(f"开始发布草稿，media_id: {media_id}")
            
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
            
            # 发布草稿
            logger.info("开始发布草稿")
            publish_result = self.draft_service.publish_draft(access_token, media_id)
            
            if publish_result and publish_result.get('errcode') == 0:
                logger.info("草稿发布成功")
                
                # 更新历史记录状态
                publish_data = {
                    'publish_id': publish_result.get('publish_id'),
                    'msg_data_id': publish_result.get('msg_data_id')
                }
                self.history_service.update_publish_status(media_id, publish_data)
                
                return {
                    'success': True,
                    'message': '草稿发布成功',
                    'data': {
                        'publish_id': publish_result.get('publish_id'),
                        'msg_data_id': publish_result.get('msg_data_id'),
                        'media_id': media_id
                    }
                }
            else:
                error_msg = publish_result.get('errmsg', '发布失败') if publish_result else '发布失败'
                logger.error(f"草稿发布失败: {error_msg}")
                return {
                    'success': False,
                    'message': f'草稿发布失败: {error_msg}'
                }
                
        except Exception as e:
            logger.error(f"发布草稿时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'发布草稿失败: {str(e)}'
            }
    
    def _process_content_images(self, content: str, access_token: str) -> dict:
        """
        处理文章内容中的图片，将本地图片上传到微信平台并替换为微信URL格式，并返回media_id和url列表
        :param content: 原始内容
        :param access_token: 微信access_token
        :return: {'content': 替换后的内容, 'images': [{'media_id':..., 'url':...}, ...]}
        """
        try:
            import re
            # 查找所有本地图片路径
            local_image_pattern = r'<img[^>]*src=["\'](cache\\[^"\']+)["\'][^>]*>'
            matches = re.findall(local_image_pattern, content)
            
            processed_content = content
            images = []
            for local_path in matches:
                # 上传图片到微信平台获取URL（用于文章内容）
                image_url = self.wechat_service.upload_article_image(access_token, local_path)
                if image_url:
                    # 替换为微信URL格式
                    img_pattern = rf'<img[^>]*src=["\']{re.escape(local_path)}["\'][^>]*>'
                    url_replacement = f'<img src="{image_url}" alt="文章配图" style="max-width: 100%; height: auto;">'
                    processed_content = re.sub(img_pattern, url_replacement, processed_content)
                    
                    # 同时上传为永久素材获取media_id（用于封面）
                    upload_result = self.wechat_service.upload_permanent_material(
                        access_token, local_path, 'image'
                    )
                    media_id = upload_result.get('media_id') if upload_result else None
                    images.append({'media_id': media_id, 'url': image_url})
                    logger.info(f"图片上传成功，本地路径: {local_path}, 微信URL: {image_url}, media_id: {media_id}")
                else:
                    logger.warning(f"图片上传失败，保持本地路径: {local_path}")
            
            return {'content': processed_content, 'images': images}
            
        except Exception as e:
            logger.error(f"处理内容图片时发生错误: {str(e)}")
            return {'content': content, 'images': []}  # 出错时返回原始内容
    
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
            
            # 只用带图内容
            preview_content = data.get('content', '')
            logger.info(f"[预览] 标题={data.get('title', 'Unknown')}, 内容前100字={preview_content[:100]}, 图片数={preview_content.count('<img')}")
            
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
    
    def _process_images_in_content(self, content: str, title: str, description: str, image_count: int, image_model: str = "gemini", ai_model: str = "gemini", custom_image_prompt: str = "", dashscope_params: dict = None, dashscope_image_model_code: str = "") -> str:
        """
        在文章内容中处理配图：生成图片并插入到合适位置，仅插入本地图片路径，不上传到公众号平台。
        :param content: 原始文章内容
        :param title: 文章标题
        :param description: 文章描述
        :param image_count: 配图数量
        :param image_model: 生图模型
        :param ai_model: AI模型（用于Pexels搜索提示词生成）
        :param custom_image_prompt: 自定义图片提示词
        :return: 插入配图后的内容
        """
        try:
            logger.info(f"开始处理文章配图，计划生成{image_count}张图片（仅本地路径，不上传微信）")
            paragraphs = content.split('</p>')
            total_paragraphs = len(paragraphs)
            if total_paragraphs < 2 or image_count < 1:
                logger.warning("文章段落过少或配图数量小于1，跳过配图插入")
                return content
            if image_count >= total_paragraphs:
                insert_positions = list(range(1, total_paragraphs))[:image_count]
            else:
                insert_positions = [round((i + 1) * total_paragraphs / (image_count + 1)) for i in range(image_count)]
            logger.info(f"计划在第{insert_positions}段后插入配图")
            generated_images = []
            if dashscope_params is None:
                dashscope_params = {}
            for i, position in enumerate(insert_positions):
                try:
                    logger.info(f"生成第{i+1}张配图，使用模型: {image_model}")
                    user_custom_prompt = custom_image_prompt
                    # dashscope模型ID优先用dashscope_params['model_name']，否则用dashscope_image_model_code
                    if image_model == 'dashscope':
                        if not dashscope_params.get('model_name') and dashscope_image_model_code:
                            dashscope_params['model_name'] = dashscope_image_model_code
                        if not dashscope_params.get('model_name'):
                            logger.error("阿里云百炼模型ID未传递")
                            return content
                    image_path = self.image_service.generate_article_image(
                        title=title,
                        description=description,
                        image_model=image_model,
                        article_content=content,
                        ai_model=ai_model,
                        image_index=i+1,
                        total_images=image_count,
                        dashscope_params=dashscope_params,
                        user_custom_prompt=user_custom_prompt
                    )
                    if image_path:
                        image_html = f'<img src="{image_path}" alt="文章配图" style="max-width: 100%; height: auto;">'
                        logger.info(f"第{i+1}张配图处理完成，使用本地路径: {image_path}")
                        generated_images.append({
                            'local_path': image_path,
                            'image_html': image_html,
                            'position': position
                        })
                    else:
                        logger.warning(f"第{i+1}张配图生成失败")
                except Exception as e:
                    logger.error(f"生成第{i+1}张配图时出错: {str(e)}")
            processed_content = content
            for img_info in sorted(generated_images, key=lambda x: -x['position']):
                position = img_info['position']
                image_html = f'<p style="text-align: center;">{img_info["image_html"]}</p>'
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
    
    def get_generation_history(self) -> Dict[str, Any]:
        """
        获取文章生成历史
        :return: 响应数据
        """
        try:
            limit = request.args.get('limit', 20, type=int)
            history = self.history_service.get_generation_history(limit)
            
            return {
                'success': True,
                'message': '获取历史记录成功',
                'data': history
            }
            
        except Exception as e:
            logger.error(f"获取生成历史时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'获取历史记录失败: {str(e)}'
            }
    
    def get_publish_history(self) -> Dict[str, Any]:
        """
        获取发布历史
        :return: 响应数据
        """
        try:
            limit = request.args.get('limit', 20, type=int)
            publish_history = self.history_service.get_publish_history(limit)
            
            return {
                'success': True,
                'message': '获取发布历史成功',
                'data': publish_history
            }
            
        except Exception as e:
            logger.error(f"获取发布历史时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'获取发布历史失败: {str(e)}'
            }
    
    def get_article_content(self) -> Dict[str, Any]:
        """
        获取指定文章的内容
        :return: 响应数据
        """
        try:
            data = request.get_json()
            if not data:
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            cache_files = data.get('cache_files', [])
            if not cache_files:
                return {
                    'success': False,
                    'message': '缺少cache文件信息'
                }
            
            content = self.history_service.get_article_content(cache_files)
            if content is None:
                return {
                    'success': False,
                    'message': '文章内容不存在'
                }
            
            return {
                'success': True,
                'message': '获取文章内容成功',
                'data': {
                    'content': content
                }
            }
            
        except Exception as e:
            logger.error(f"获取文章内容时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'获取文章内容失败: {str(e)}'
            }
    
    def _clean_ai_generated_content(self, content: str) -> str:
        """
        清理AI生成内容中的多余部分，只保留正文HTML，去除AI附加说明、代码块标记等
        :param content: 原始内容
        :return: 清理后的内容
        """
        try:
            import re
            from bs4 import BeautifulSoup
            logger.info("开始清理AI生成内容（修正版）")
            original_length = len(content)
            
            # 1. 删除开头的 ```html 标记
            content = re.sub(r'^```html\s*', '', content, flags=re.IGNORECASE | re.MULTILINE)
            
            # 2. 找到最后一个</div>的位置，只保留到这里
            last_div_idx = content.rfind('</div>')
            if last_div_idx != -1:
                content = content[:last_div_idx + len('</div>')]
                logger.info(f"找到最后一个</div>，截断到位置: {last_div_idx + len('</div>')}")
            else:
                logger.warning("未找到</div>标签，保留全部内容")
            
            # 3. 处理样式内联化（新增）
            content = self._inline_styles(content)
            
            # 4. 清理多余空白
            content = content.strip()
            
            cleaned_length = len(content)
            removed_chars = original_length - cleaned_length
            
            if cleaned_length == 0:
                logger.error("清理后内容为空，返回原始内容")
                return content  # 如果清理后为空，返回原始内容
            elif removed_chars > 0:
                logger.info(f"内容清理完成，移除了 {removed_chars} 个字符，清理后长度: {cleaned_length}")
            else:
                logger.info("内容清理完成，未发现需要清理的内容")
            
            return content
            
        except Exception as e:
            logger.error(f"清理AI生成内容时发生错误: {str(e)}")
            return content  # 出错时返回原始内容
    
    def _inline_styles(self, content: str) -> str:
        """
        将<style>标签中的CSS样式转换为内联样式
        :param content: 原始HTML内容
        :return: 内联样式后的HTML内容
        """
        try:
            from bs4 import BeautifulSoup
            import re
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找<style>标签
            style_tags = soup.find_all('style')
            if not style_tags:
                logger.info("未发现<style>标签，无需内联处理")
                return content
            
            logger.info(f"发现{len(style_tags)}个<style>标签，开始内联处理")
            
            # 收集所有CSS规则
            css_rules = []
            for style_tag in style_tags:
                css_text = style_tag.get_text()
                # 解析CSS规则
                rules = self._parse_css_rules(css_text)
                css_rules.extend(rules)
                # 删除<style>标签
                style_tag.decompose()
            
            # 应用CSS规则到对应的HTML元素
            for selector, properties in css_rules:
                elements = soup.select(selector)
                for element in elements:
                    # 获取现有样式
                    existing_style = element.get('style', '')
                    # 合并新样式
                    new_style = self._merge_styles(existing_style, properties)
                    element['style'] = new_style
            
            logger.info(f"样式内联处理完成，应用了{len(css_rules)}个CSS规则")
            return str(soup)
            
        except Exception as e:
            logger.error(f"样式内联处理时发生错误: {str(e)}")
            return content
    
    def _parse_css_rules(self, css_text: str) -> list:
        """
        解析CSS文本，提取选择器和属性
        :param css_text: CSS文本
        :return: [(selector, properties_dict), ...]
        """
        import re
        
        rules = []
        # 移除注释和多余空白
        css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
        css_text = re.sub(r'\s+', ' ', css_text)
        
        # 匹配CSS规则
        pattern = r'([^{]+)\{([^}]+)\}'
        matches = re.findall(pattern, css_text)
        
        for selector, properties_text in matches:
            selector = selector.strip()
            properties = {}
            
            # 解析属性
            for prop in properties_text.split(';'):
                prop = prop.strip()
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    properties[key.strip()] = value.strip()
            
            if properties:
                rules.append((selector, properties))
        
        return rules
    
    def _merge_styles(self, existing_style: str, new_properties: dict) -> str:
        """
        合并现有样式和新属性
        :param existing_style: 现有样式字符串
        :param new_properties: 新属性字典
        :return: 合并后的样式字符串
        """
        # 解析现有样式
        existing_props = {}
        if existing_style:
            for prop in existing_style.split(';'):
                prop = prop.strip()
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    existing_props[key.strip()] = value.strip()
        
        # 合并属性（新属性覆盖旧属性）
        merged_props = {**existing_props, **new_properties}
        
        # 转换为样式字符串
        style_parts = [f"{key}: {value}" for key, value in merged_props.items()]
        return '; '.join(style_parts)

    def get_local_version(self):
        """
        获取本地代码的git commit sha
        """
        import subprocess
        try:
            sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
            return {'success': True, 'sha': sha}
        except Exception as e:
            logger.error(f"获取本地版本失败: {e}")
            return {'success': False, 'message': str(e)}

    def update_from_github(self):
        """
        自动拉取GitHub主分支最新代码
        """
        import subprocess
        try:
            # 检查本地是否有未提交或未推送的更改
            status_output = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8').strip()
            if status_output:
                return {'success': False, 'message': '检测到本地有未提交的更改，请先处理后再更新。', 'needs_confirm': True}

            # 拉取最新代码
            pull = subprocess.check_output(['git', 'pull', 'origin', 'main']).decode('utf-8').strip()
            # 可选：重启服务（如需）
            return {'success': True, 'message': pull}
        except Exception as e:
            logger.error(f"自动更新失败: {e}")
            return {'success': False, 'message': str(e)}