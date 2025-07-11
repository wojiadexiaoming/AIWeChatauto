"""
微信服务模块
处理微信公众号API相关操作
"""

import requests
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class WeChatService:
    """微信服务类"""
    
    def __init__(self):
        self.base_url = AppConfig.WECHAT_BASE_URL
        self.timeout = AppConfig.API_TIMEOUT
        logger.info("微信服务初始化完成")
    
    def get_access_token(self, appid: str, appsecret: str) -> Optional[Dict[str, Any]]:
        """
        获取微信access_token
        :param appid: 公众号的AppID
        :param appsecret: 公众号的AppSecret
        :return: 返回token信息字典
        """
        url = f"{self.base_url}/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': appid,
            'secret': appsecret
        }
        
        try:
            logger.info(f"开始获取access_token，AppID: {appid}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if 'access_token' in result:
                expires_in = result['expires_in']
                expire_time = int(time.time()) + expires_in
                
                token_info = {
                    'access_token': result['access_token'],
                    'expires_in': expires_in,
                    'expire_time': expire_time,
                    'expire_time_str': datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S'),
                    'appid': appid,
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                logger.info(f"access_token获取成功，有效期: {expires_in}秒")
                return token_info
            else:
                error_code = result.get('errcode', 'unknown')
                error_msg = result.get('errmsg', 'unknown error')
                logger.error(f"获取access_token失败，错误码: {error_code}, 错误信息: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"获取access_token网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取access_token时发生异常: {str(e)}")
            return None
    
    def upload_article_image(self, access_token: str, image_path: str) -> Optional[str]:
        """
        上传图文消息内的图片获取URL
        :param access_token: 访问令牌
        :param image_path: 图片文件路径
        :return: 图片URL
        """
        url = f"{self.base_url}/cgi-bin/media/uploadimg"
        params = {'access_token': access_token}
        
        try:
            logger.info(f"开始上传图文消息图片: {image_path}")
            
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, params=params, files=files, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                
                if 'url' in result:
                    image_url = result['url']
                    logger.info(f"图片上传成功，URL: {image_url}")
                    return image_url
                else:
                    error_code = result.get('errcode', 'unknown')
                    error_msg = result.get('errmsg', 'unknown error')
                    logger.error(f"上传图文消息图片失败，错误码: {error_code}, 错误信息: {error_msg}")
                    return None
                    
        except FileNotFoundError:
            logger.error(f"图片文件不存在: {image_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传图片网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"上传图文消息图片时发生异常: {str(e)}")
            return None
    
    def upload_permanent_material(self, access_token: str, file_path: str, 
                                material_type: str, description: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        新增永久素材
        :param access_token: 访问令牌
        :param file_path: 文件路径
        :param material_type: 素材类型(image/voice/video/thumb)
        :param description: 视频素材描述(仅视频素材需要)
        :return: 素材信息
        """
        url = f"{self.base_url}/cgi-bin/material/add_material"
        params = {
            'access_token': access_token,
            'type': material_type
        }
        
        try:
            logger.info(f"开始上传永久素材: {file_path}, 类型: {material_type}")
            
            with open(file_path, 'rb') as f:
                files = {'media': f}
                data = None
                
                if material_type == 'video' and description:
                    description_json = json.dumps(description, ensure_ascii=False)
                    files['description'] = (None, description_json)
                
                response = requests.post(url, params=params, files=files, data=data, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                
                if 'media_id' in result:
                    logger.info(f"永久素材上传成功，media_id: {result['media_id']}")
                    return result
                else:
                    error_code = result.get('errcode', 'unknown')
                    error_msg = result.get('errmsg', 'unknown error')
                    logger.error(f"上传永久素材失败，错误码: {error_code}, 错误信息: {error_msg}")
                    return None
                    
        except FileNotFoundError:
            logger.error(f"素材文件不存在: {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传素材网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"上传永久素材时发生异常: {str(e)}")
            return None
    
    def test_connection(self, appid: str, appsecret: str) -> Dict[str, Any]:
        """
        测试微信API连接
        :param appid: 公众号AppID
        :param appsecret: 公众号AppSecret
        :return: 测试结果
        """
        logger.info("开始测试微信API连接")
        
        token_info = self.get_access_token(appid, appsecret)
        
        if token_info and token_info.get('access_token'):
            logger.info("微信API连接测试成功")
            return {
                'success': True,
                'message': '微信API连接成功',
                'data': {
                    'access_token': token_info['access_token'][:20] + '...',
                    'expires_in': token_info['expires_in']
                }
            }
        else:
            logger.error("微信API连接测试失败")
            return {
                'success': False,
                'message': '微信API连接失败，请检查AppID和AppSecret是否正确'
            }