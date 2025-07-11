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
                logger.error("请求数据为空")
                return {
                    'success': False,
                    'message': '请求数据为空'
                }
            
            logger.info("开始保存配置")
            logger.info(f"接收到的配置数据: {config_data}")
            
            # 验证必填字段
            validation_result = self._validate_config_data(config_data)
            if not validation_result['valid']:
                logger.error(f"配置验证失败: {validation_result['message']}")
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # 保存配置
            save_result = self.config_service.save_config(config_data)
            logger.info(f"配置保存结果: {save_result}")
            
            if save_result:
                # 验证保存是否成功
                saved_config = self.config_service.load_config()
                logger.info(f"保存后读取的配置: {saved_config}")
                
                logger.info("配置保存成功")
                return {
                    'success': True,
                    'message': '配置保存成功',
                    'data': saved_config
                }
            else:
                logger.error("配置保存失败")
                return {
                    'success': False,
                    'message': '配置保存失败'
                }
                
        except Exception as e:
            logger.error(f"保存配置时发生错误: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'保存配置失败: {str(e)}'
            }
    
    def _validate_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置数据"""
        logger.info(f"开始验证配置数据: {config_data}")
        
        # 检查必填字段，但允许部分为空以支持分步配置
        required_fields = {
            'wechat_appid': '微信AppID',
            'wechat_appsecret': '微信AppSecret', 
            'gemini_api_key': 'Gemini API密钥'
        }
        
        # 只验证存在且非空的字段
        for field, label in required_fields.items():
            if field in config_data and config_data[field]:
                value = config_data[field]
                if not isinstance(value, str) or not value.strip():
                    logger.error(f"字段 {field} 值无效: {value}")
                    return {
                        'valid': False,
                        'message': f'{label}格式错误'
                    }
                
                # 验证微信AppID格式（如果提供）
                if field == 'wechat_appid':
                    wechat_appid = value.strip()
                    if not wechat_appid.startswith('wx') or len(wechat_appid) != 18:
                        return {
                            'valid': False,
                            'message': '微信AppID格式不正确，应为wx开头的18位字符'
                        }
                
                # 验证Gemini API密钥格式（如果提供）
                if field == 'gemini_api_key':
                    gemini_api_key = value.strip()
                    if not gemini_api_key.startswith('AIza'):
                        return {
                            'valid': False,
                            'message': 'Gemini API密钥格式不正确，应以AIza开头'
                        }
        
        logger.info("配置数据验证通过")
        return {'valid': True}
    
    def test_wechat_connection(self) -> Dict[str, Any]:
        """测试微信连接"""
        try:
            logger.info("开始测试微信API连接")
            
            # 获取当前配置
            config = self.config_service.load_config()
            logger.info(f"当前完整配置: {config}")
            
            wechat_config = self.config_service.get_wechat_config()
            logger.info(f"微信配置: appid={wechat_config.get('appid', 'None')[:10]}..., appsecret={'已设置' if wechat_config.get('appsecret') else '未设置'}")
            
            if not wechat_config['appid'] or not wechat_config['appsecret']:
                logger.error(f"微信配置不完整: appid={bool(wechat_config.get('appid'))}, appsecret={bool(wechat_config.get('appsecret'))}")
                return {
                    'success': False,
                    'message': '请先配置微信公众号信息',
                    'debug_info': {
                        'has_appid': bool(wechat_config.get('appid')),
                        'has_appsecret': bool(wechat_config.get('appsecret')),
                        'config_keys': list(config.keys())
                    }
                }
            
            result = self.wechat_service.test_connection(
                wechat_config['appid'],
                wechat_config['appsecret']
            )
            
            logger.info(f"微信连接测试完整结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"测试微信连接时发生错误: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'测试失败: {str(e)}'
            }
    
    def test_gemini_connection(self) -> Dict[str, Any]:
        """测试Gemini连接"""
        try:
            logger.info("开始测试Gemini AI连接")
            
            # 获取当前配置
            config = self.config_service.load_config()
            logger.info(f"当前完整配置: {config}")
            
            gemini_config = self.config_service.get_gemini_config()
            logger.info(f"Gemini配置: api_key={'已设置' if gemini_config.get('api_key') else '未设置'}, model={gemini_config.get('model', 'None')}")
            
            if not gemini_config['api_key']:
                logger.error(f"Gemini API密钥未配置")
                return {
                    'success': False,
                    'message': '请先配置Gemini API密钥',
                    'debug_info': {
                        'has_api_key': bool(gemini_config.get('api_key')),
                        'config_keys': list(config.keys())
                    }
                }
            
            # 设置API密钥
            self.gemini_service.set_api_key(gemini_config['api_key'])
            
            result = self.gemini_service.test_connection(gemini_config['model'])
            
            logger.info(f"Gemini连接测试完整结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"测试Gemini连接时发生错误: {str(e)}", exc_info=True)
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