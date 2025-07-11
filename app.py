import os
import logging
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from wechat_api import WeChatAPI
from gemini_service import GeminiService
from config_manager import ConfigManager

# 配置日志
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "wechat-gemini-publisher-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# 创建必要的目录
os.makedirs('cache', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# 初始化服务
config_manager = ConfigManager()
wechat_api = WeChatAPI()
gemini_service = GeminiService()

@app.route('/')
def index():
    """主页面"""
    logger.info("访问主页面")
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """处理配置信息"""
    if request.method == 'GET':
        try:
            config = config_manager.load_config()
            logger.info("成功加载配置信息")
            return jsonify({
                'success': True,
                'data': config
            })
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'加载配置失败: {str(e)}'
            })
    
    elif request.method == 'POST':
        try:
            config_data = request.json
            logger.info(f"接收到配置数据: {json.dumps(config_data, ensure_ascii=False)}")
            
            # 验证必填字段
            required_fields = ['wechat_appid', 'wechat_appsecret', 'gemini_api_key', 'gemini_model']
            for field in required_fields:
                if not config_data.get(field):
                    return jsonify({
                        'success': False,
                        'message': f'缺少必填字段: {field}'
                    })
            
            # 保存配置
            config_manager.save_config(config_data)
            logger.info("配置保存成功")
            
            return jsonify({
                'success': True,
                'message': '配置保存成功'
            })
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存配置失败: {str(e)}'
            })

@app.route('/api/test-wechat', methods=['POST'])
def test_wechat():
    """测试微信API连接"""
    try:
        config = config_manager.load_config()
        appid = config.get('wechat_appid')
        appsecret = config.get('wechat_appsecret')
        
        if not appid or not appsecret:
            return jsonify({
                'success': False,
                'message': '请先配置微信公众号信息'
            })
        
        logger.info("开始测试微信API连接")
        token_info = wechat_api.get_access_token(appid, appsecret)
        
        if token_info and token_info.get('access_token'):
            logger.info("微信API连接测试成功")
            return jsonify({
                'success': True,
                'message': '微信API连接成功',
                'data': {
                    'access_token': token_info['access_token'][:20] + '...',
                    'expires_in': token_info['expires_in']
                }
            })
        else:
            logger.error("微信API连接测试失败")
            return jsonify({
                'success': False,
                'message': '微信API连接失败，请检查AppID和AppSecret'
            })
            
    except Exception as e:
        logger.error(f"测试微信API时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        })

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    """测试Gemini AI连接"""
    try:
        config = config_manager.load_config()
        api_key = config.get('gemini_api_key')
        model = config.get('gemini_model')
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': '请先配置Gemini API密钥'
            })
        
        logger.info("开始测试Gemini AI连接")
        
        # 设置环境变量
        os.environ['GEMINI_API_KEY'] = api_key
        
        # 测试生成内容
        test_content = gemini_service.generate_content("请说'测试成功'", model or "gemini-2.5-flash")
        
        if test_content and "测试成功" in test_content:
            logger.info("Gemini AI连接测试成功")
            return jsonify({
                'success': True,
                'message': 'Gemini AI连接成功',
                'data': {
                    'response': test_content
                }
            })
        else:
            logger.error("Gemini AI连接测试失败")
            return jsonify({
                'success': False,
                'message': 'Gemini AI连接失败，请检查API密钥'
            })
            
    except Exception as e:
        logger.error(f"测试Gemini AI时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        })

@app.route('/api/generate-article', methods=['POST'])
def generate_article():
    """生成文章"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({
                'success': False,
                'message': '请输入文章标题'
            })
        
        config = config_manager.load_config()
        api_key = config.get('gemini_api_key')
        model = config.get('gemini_model', 'gemini-2.5-flash')
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': '请先配置Gemini API密钥'
            })
        
        # 设置环境变量
        os.environ['GEMINI_API_KEY'] = api_key
        
        logger.info(f"开始生成文章，标题: {title}")
        
        # 生成文章内容
        content = gemini_service.generate_article_content(title, model)
        if not content:
            return jsonify({
                'success': False,
                'message': '文章内容生成失败'
            })
        
        # 生成文章摘要
        digest = gemini_service.generate_digest(title, content, model)
        
        # 生成配图
        image_url = None
        try:
            logger.info("开始生成配图")
            image_path = gemini_service.generate_article_image(title, model)
            if image_path:
                image_url = f"/cache/{os.path.basename(image_path)}"
                logger.info(f"配图生成成功: {image_path}")
        except Exception as e:
            logger.warning(f"配图生成失败: {str(e)}")
        
        logger.info("文章生成完成")
        
        return jsonify({
            'success': True,
            'message': '文章生成成功',
            'data': {
                'title': title,
                'content': content,
                'digest': digest,
                'image_url': image_url,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        logger.error(f"生成文章时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'生成文章失败: {str(e)}'
        })

@app.route('/api/publish-article', methods=['POST'])
def publish_article():
    """发布文章到微信公众号"""
    try:
        data = request.json
        article_data = data.get('article')
        
        if not article_data:
            return jsonify({
                'success': False,
                'message': '缺少文章数据'
            })
        
        config = config_manager.load_config()
        appid = config.get('wechat_appid')
        appsecret = config.get('wechat_appsecret')
        
        if not appid or not appsecret:
            return jsonify({
                'success': False,
                'message': '请先配置微信公众号信息'
            })
        
        logger.info("开始发布文章到微信公众号")
        
        # 获取access_token
        token_info = wechat_api.get_access_token(appid, appsecret)
        if not token_info or not token_info.get('access_token'):
            return jsonify({
                'success': False,
                'message': '获取微信access_token失败'
            })
        
        access_token = token_info['access_token']
        
        # 上传配图（如果有）
        thumb_media_id = None
        if article_data.get('image_url'):
            image_path = article_data['image_url'].replace('/cache/', 'cache/')
            if os.path.exists(image_path):
                logger.info(f"开始上传配图: {image_path}")
                upload_result = wechat_api.upload_permanent_material(access_token, image_path, 'image')
                if upload_result and upload_result.get('media_id'):
                    thumb_media_id = upload_result['media_id']
                    logger.info(f"配图上传成功，media_id: {thumb_media_id}")
                else:
                    logger.warning("配图上传失败")
        
        # 创建草稿
        draft_data = {
            "articles": [{
                "title": article_data['title'],
                "author": config.get('author', 'AI笔记'),
                "digest": article_data.get('digest', ''),
                "content": article_data['content'],
                "content_source_url": config.get('content_source_url', ''),
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": 1 if thumb_media_id else 0,
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }]
        }
        
        logger.info("开始创建草稿")
        draft_result = wechat_api.add_draft(access_token, draft_data)
        
        if not draft_result or not draft_result.get('media_id'):
            return jsonify({
                'success': False,
                'message': '创建草稿失败'
            })
        
        media_id = draft_result['media_id']
        logger.info(f"草稿创建成功，media_id: {media_id}")
        
        # 发布草稿
        logger.info("开始发布草稿")
        publish_result = wechat_api.publish_draft(access_token, media_id)
        
        if publish_result and publish_result.get('errcode') == 0:
            logger.info("文章发布成功")
            return jsonify({
                'success': True,
                'message': '文章发布成功',
                'data': {
                    'publish_id': publish_result.get('publish_id'),
                    'msg_data_id': publish_result.get('msg_data_id'),
                    'media_id': media_id
                }
            })
        else:
            error_msg = publish_result.get('errmsg', '发布失败') if publish_result else '发布失败'
            logger.error(f"文章发布失败: {error_msg}")
            return jsonify({
                'success': False,
                'message': f'文章发布失败: {error_msg}'
            })
            
    except Exception as e:
        logger.error(f"发布文章时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'发布文章失败: {str(e)}'
        })

@app.route('/cache/<filename>')
def serve_cache_file(filename):
    """提供缓存文件访问"""
    return send_from_directory('cache', filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '页面未找到'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"服务器内部错误: {str(error)}")
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    logger.info("启动微信公众号AI发布系统")
    app.run(host='0.0.0.0', port=5000, debug=True)
