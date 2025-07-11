import requests
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class WeChatAPI:
    """微信公众号API封装"""
    
    def __init__(self):
        self.base_url = "https://api.weixin.qq.com"
    
    def get_access_token(self, appid, appsecret):
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
            logger.info(f"获取access_token，AppID: {appid}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'access_token' in result:
                logger.info(f"获取access_token成功，有效期: {result['expires_in']}秒")
                return {
                    'access_token': result['access_token'],
                    'expires_in': result['expires_in'],
                    'expire_time': int(time.time()) + result['expires_in'],
                    'expire_time_str': datetime.fromtimestamp(int(time.time()) + result['expires_in']).strftime('%Y-%m-%d %H:%M:%S'),
                    'appid': appid,
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                error_code = result.get('errcode', 'unknown')
                error_msg = result.get('errmsg', 'unknown error')
                logger.error(f"获取access_token失败，错误码: {error_code}, 错误信息: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"获取access_token时发生异常: {str(e)}")
            return None
    
    def upload_article_image(self, access_token, image_path):
        """
        上传图文消息内的图片获取URL
        :param access_token: 访问令牌
        :param image_path: 图片文件路径
        :return: 图片URL
        """
        url = f"{self.base_url}/cgi-bin/media/uploadimg"
        params = {'access_token': access_token}
        
        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                logger.info(f"上传图文消息图片: {image_path}")
                response = requests.post(url, params=params, files=files, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                if 'url' in result:
                    logger.info(f"图片上传成功，URL: {result['url']}")
                    return result['url']
                else:
                    error_code = result.get('errcode', 'unknown')
                    error_msg = result.get('errmsg', 'unknown error')
                    logger.error(f"上传图文消息图片失败，错误码: {error_code}, 错误信息: {error_msg}")
                    return None
                    
        except Exception as e:
            logger.error(f"上传图文消息图片时发生异常: {str(e)}")
            return None
    
    def upload_permanent_material(self, access_token, file_path, material_type, description=None):
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
            with open(file_path, 'rb') as f:
                files = {'media': f}
                data = None
                
                if material_type == 'video' and description:
                    if isinstance(description, dict):
                        description = json.dumps(description, ensure_ascii=False)
                    files['description'] = (None, description)
                
                logger.info(f"上传永久素材: {file_path}, 类型: {material_type}")
                response = requests.post(url, params=params, files=files, data=data, timeout=60)
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
                    
        except Exception as e:
            logger.error(f"上传永久素材时发生异常: {str(e)}")
            return None
    
    def add_draft(self, access_token, draft_data):
        """
        新增草稿
        :param access_token: 访问令牌
        :param draft_data: 草稿数据
        :return: 草稿信息
        """
        url = f"{self.base_url}/cgi-bin/draft/add"
        params = {'access_token': access_token}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        
        try:
            logger.info("创建草稿")
            logger.debug(f"草稿数据: {json.dumps(draft_data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                url, 
                params=params,
                data=json.dumps(draft_data, ensure_ascii=False), 
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            if 'media_id' in result:
                logger.info(f"草稿创建成功，media_id: {result['media_id']}")
                return result
            else:
                error_code = result.get('errcode', 'unknown')
                error_msg = result.get('errmsg', 'unknown error')
                logger.error(f"创建草稿失败，错误码: {error_code}, 错误信息: {error_msg}")
                return result
                
        except Exception as e:
            logger.error(f"创建草稿时发生异常: {str(e)}")
            return None
    
    def publish_draft(self, access_token, media_id):
        """
        发布草稿
        :param access_token: 访问令牌
        :param media_id: 草稿media_id
        :return: 发布结果
        """
        url = f"{self.base_url}/cgi-bin/freepublish/submit"
        params = {'access_token': access_token}
        payload = {"media_id": media_id}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        
        try:
            logger.info(f"发布草稿，media_id: {media_id}")
            
            response = requests.post(
                url,
                params=params,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            error_code = result.get('errcode', -1)
            error_msg = result.get('errmsg', 'unknown error')
            
            if error_code == 0:
                logger.info(f"草稿发布成功，publish_id: {result.get('publish_id')}")
            else:
                logger.error(f"草稿发布失败，错误码: {error_code}, 错误信息: {error_msg}")
            
            return result
            
        except Exception as e:
            logger.error(f"发布草稿时发生异常: {str(e)}")
            return None
