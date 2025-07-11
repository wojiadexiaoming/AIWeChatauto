"""
配置控制器模块
处理配置相关的HTTP请求
"""

import logging
from flask import request, jsonify
from typing import Dict, Any
from services.config_service import ConfigService
from services.wechat_service import WeChatService
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ConfigController:
    """配置控制器类"""
    
    def __init__(self):
        self.config_service = ConfigService()
        self.wechat_service = WeChatService()
        self.gemini_service = GeminiService()
        logger.info("配置控制器初始化完成")
    
    def handle_config_request(self) -> Dict[str, Any]:
        """
        处理配置请求
        :return: 响应数据
        """
        try:
            if request.method == 'GET':
                return self._get_config()
            elif request.method == 'POST':
                return self._save_config()
            else:
                return {
                    'success': False,
                    'message': '不支持的请求方法'
                }
        except Exception as e:
            logger.error(f"处理配置请求时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }
    
    def _get_config(self) -> Dict[str, Any]:
        """获取配置"""
        try:
            logger.info("开始获取配置信息")
            config = self.config_service.load_config()
            
            # 不返回敏感信息的完整内容
            safe_config = config.copy()
            if safe_config.get('wechat_appsecret'):
                safe_config['wechat_appsecret'] = '***' + safe_config['wechat_appsecret'][-4:]
            if safe_config.get('gemini_api_key'):
                safe_config['gemini_api_key'] = '***' + safe_config['gemini_api_key'][-4:]
            
            logger.info("配置信息获取成功")
            return {
                'success': True,
                'data': safe_config,
                'message': '配置加载成功'
            }
            
        except Exception as e:
            logger.error(f"获取配置时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'加载配置失败: {str(e)}'
            }
    
    def _save_config(self) -> Dict[str, Any]:
        """保存配置"""
        try:
            config_data = request.get_json()
            if not config_data:
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            logger.info("开始保存配置")
            logger.debug(f"配置数据字段: {list(config_data.keys())}")
            
            # 验证必填字段
            validation_result = self._validate_config_data(config_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # 保存配置
            if self.config_service.save_config(config_data):
                logger.info("配置保存成功")
                return {
                    'success': True,
                    'message': '配置保存成功'
                }
            else:
                logger.error("配置保存失败")
                return {
                    'success': False,
                    'message': '配置保存失败'
                }
                
        except Exception as e:
            logger.error(f"保存配置时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'保存配置失败: {str(e)}'
            }
    
    def _validate_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置数据"""
        required_fields = {
            'wechat_appid': '微信AppID',
            'wechat_appsecret': '微信AppSecret',
            'gemini_api_key': 'Gemini API密钥'
        }
        
        for field, label in required_fields.items():
            if field not in config_data:
                return {
                    'valid': False,
                    'message': f'缺少必填字段: {label}'
                }
            
            value = config_data[field]
            if not isinstance(value, str) or not value.strip():
                return {
                    'valid': False,
                    'message': f'{label}不能为空'
                }
        
        # 验证微信AppID格式
        wechat_appid = config_data['wechat_appid'].strip()
        if not wechat_appid.startswith('wx') or len(wechat_appid) != 18:
            return {
                'valid': False,
                'message': '微信AppID格式不正确，应为wx开头的18位字符'
            }
        
        # 验证Gemini API密钥格式
        gemini_api_key = config_data['gemini_api_key'].strip()
        if not gemini_api_key.startswith('AIza'):
            return {
                'valid': False,
                'message': 'Gemini API密钥格式不正确，应以AIza开头'
            }
        
        return {'valid': True}
    
    def test_wechat_connection(self) -> Dict[str, Any]:
        """测试微信连接"""
        try:
            logger.info("开始测试微信API连接")
            
            wechat_config = self.config_service.get_wechat_config()
            if not wechat_config['appid'] or not wechat_config['appsecret']:
                return {
                    'success': False,
                    'message': '请先配置微信公众号信息'
                }
            
            result = self.wechat_service.test_connection(
                wechat_config['appid'],
                wechat_config['appsecret']
            )
            
            logger.info(f"微信连接测试结果: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"测试微信连接时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'测试失败: {str(e)}'
            }
    
    def test_gemini_connection(self) -> Dict[str, Any]:
        """测试Gemini连接"""
        try:
            logger.info("开始测试Gemini AI连接")
            
            gemini_config = self.config_service.get_gemini_config()
            if not gemini_config['api_key']:
                return {
                    'success': False,
                    'message': '请先配置Gemini API密钥'
                }
            
            # 设置API密钥
            self.gemini_service.set_api_key(gemini_config['api_key'])
            
            result = self.gemini_service.test_connection(gemini_config['model'])
            
            logger.info(f"Gemini连接测试结果: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"测试Gemini连接时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'测试失败: {str(e)}'
            }
    
    def get_config_status(self) -> Dict[str, Any]:
        """获取配置状态"""
        try:
            status = self.config_service.get_config_status()
            
            return {
                'success': True,
                'data': status,
                'message': '配置状态获取成功'
            }
            
        except Exception as e:
            logger.error(f"获取配置状态时发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'获取配置状态失败: {str(e)}'
            }