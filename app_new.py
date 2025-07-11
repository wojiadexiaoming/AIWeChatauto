"""
主应用文件
基于Flask的微信公众号AI发布系统
"""

import os
from flask import Flask, render_template, send_from_directory, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

# 导入配置和服务
from config.app_config import AppConfig, setup_logging
from controllers.config_controller import ConfigController
from controllers.article_controller import ArticleController

# 设置日志
logger = setup_logging()

# 创建Flask应用
app = Flask(__name__)
app.secret_key = AppConfig.SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# 创建必要的目录
AppConfig.create_directories()

# 初始化控制器
config_controller = ConfigController()
article_controller = ArticleController()

# 设置Gemini API密钥
os.environ['GEMINI_API_KEY'] = 'AIzaSyDBbZXB_JnMyTM9QrgOVKpQXgWnjWuvPCA'

@app.route('/')
def index():
    """主页面"""
    logger.info("访问主页面")
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """处理配置信息"""
    logger.info(f"处理配置请求: {request.method}")
    result = config_controller.handle_config_request()
    return jsonify(result)

@app.route('/api/test-wechat', methods=['POST'])
def test_wechat():
    """测试微信API连接"""
    logger.info("测试微信API连接")
    result = config_controller.test_wechat_connection()
    return jsonify(result)

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    """测试Gemini AI连接"""
    logger.info("测试Gemini AI连接")
    result = config_controller.test_gemini_connection()
    return jsonify(result)

@app.route('/api/generate-article', methods=['POST'])
def generate_article():
    """生成文章"""
    logger.info("生成文章请求")
    result = article_controller.generate_article()
    return jsonify(result)

@app.route('/api/publish-article', methods=['POST'])
def publish_article():
    """发布文章到微信公众号"""
    logger.info("发布文章请求")
    result = article_controller.publish_article()
    return jsonify(result)

@app.route('/api/config-status', methods=['GET'])
def get_config_status():
    """获取配置状态"""
    logger.info("获取配置状态")
    result = config_controller.get_config_status()
    return jsonify(result)

@app.route('/cache/<filename>')
def serve_cache_file(filename):
    """提供缓存文件访问"""
    logger.info(f"访问缓存文件: {filename}")
    return send_from_directory(AppConfig.CACHE_FOLDER, filename)

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    logger.warning(f"404错误: {request.url}")
    return jsonify({
        'success': False,
        'message': '页面未找到'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"服务器内部错误: {str(error)}")
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

@app.before_request
def before_request():
    """请求前处理"""
    from flask import request
    logger.info(f"请求: {request.method} {request.path}")

if __name__ == '__main__':
    logger.info("启动微信公众号AI发布系统")
    app.run(host='0.0.0.0', port=5000, debug=AppConfig.DEBUG)