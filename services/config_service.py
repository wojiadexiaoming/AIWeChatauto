<<<<<<< HEAD
"""
配置服务模块
处理应用配置的加载、保存和验证
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import threading
import time

logger = logging.getLogger(__name__)

class ConfigService:
    """配置服务类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        self._start_token_monitor_thread()
        logger.info(f"配置服务初始化完成，配置文件: {self.config_file}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "wechat_appid": "",
            "wechat_appsecret": "",
            "gemini_api_key": "",
            "gemini_model": "gemini-2.5-flash",
            "deepseek_api_key": "",
            "deepseek_model": "deepseek-chat",
            "dashscope_api_key": "",
            "dashscope_model": "qwen-turbo",
            "pexels_api_key": "",
            "coze_token": "",  # 新增coze令牌
            "image_model": "gemini",  # 默认生图模型
            "author": "AI笔记",
            "content_source_url": "",
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("从文件加载配置成功")
                    
                # 合并默认配置，确保所有必要字段存在
                merged_config = self.default_config.copy()
                merged_config.update(config)
                
                return merged_config
            else:
                logger.info("配置文件不存在，使用默认配置")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"加载配置时发生错误: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 验证配置数据
            if not self._validate_config(config_data):
                logger.error("配置数据验证失败")
                return False
            
            # 加载现有配置
            current_config = self.load_config()
            
            # 更新配置
            current_config.update(config_data)
            current_config["updated_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果是首次创建，设置创建时间
            if not os.path.exists(self.config_file):
                current_config["created_at"] = current_config["updated_at"]
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, ensure_ascii=False, indent=4)
            
            logger.info("配置保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存配置时发生错误: {str(e)}")
            return False
    
    def _validate_config(self, config_data: Dict[str, Any]) -> bool:
        """验证配置数据"""
        required_fields = ['wechat_appid', 'wechat_appsecret', 'gemini_api_key']
        
        for field in required_fields:
            if field in config_data:
                value = config_data[field]
                if not isinstance(value, str) or not value.strip():
                    logger.error(f"必填字段 {field} 不能为空")
                    return False
        
        # 验证模型名称
        if 'gemini_model' in config_data:
            valid_models = ['gemini-2.5-flash', 'gemini-2.5-pro']
            if config_data['gemini_model'] not in valid_models:
                logger.warning(f"未知的Gemini模型: {config_data['gemini_model']}")
        
        return True
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取单个配置值"""
        try:
            config = self.load_config()
            return config.get(key, default)
        except Exception as e:
            logger.error(f"获取配置值时发生错误: {str(e)}")
            return default
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """设置单个配置值"""
        try:
            config = self.load_config()
            config[key] = value
            return self.save_config(config)
        except Exception as e:
            logger.error(f"设置配置值时发生错误: {str(e)}")
            return False
    
    def get_wechat_config(self) -> Dict[str, str]:
        """获取微信配置"""
        config = self.load_config()
        return {
            'appid': config.get('wechat_appid', ''),
            'appsecret': config.get('wechat_appsecret', '')
        }
    
    def get_gemini_config(self) -> Dict[str, str]:
        """获取Gemini配置"""
        config = self.load_config()
        return {
            'api_key': config.get('gemini_api_key', ''),
            'model': config.get('gemini_model', 'gemini-2.5-flash')
        }
    
    def get_deepseek_config(self) -> Dict[str, str]:
        """获取DeepSeek配置"""
        config = self.load_config()
        return {
            'api_key': config.get('deepseek_api_key', ''),
            'model': config.get('deepseek_model', 'deepseek-chat')
        }
    
    def get_dashscope_config(self) -> Dict[str, str]:
        """获取阿里云百炼配置"""
        config = self.load_config()
        return {
            'api_key': config.get('dashscope_api_key', ''),
            'model': config.get('dashscope_model', 'qwen-turbo')
        }
    
    def get_pexels_config(self) -> Dict[str, str]:
        """获取Pexels配置"""
        config = self.load_config()
        return {
            'api_key': config.get('pexels_api_key', '')
        }
    
    def get_coze_config(self) -> Dict[str, str]:
        """获取Coze配置"""
        config = self.load_config()
        return {
            'coze_token': config.get('coze_token', ''),
            'coze_workflow_id': config.get('coze_workflow_id', '')
        }
    
    def get_author_config(self) -> Dict[str, str]:
        """获取作者配置"""
        config = self.load_config()
        return {
            'author': config.get('author', 'AI笔记'),
            'content_source_url': config.get('content_source_url', '')
        }
    
    def is_wechat_configured(self) -> bool:
        """检查微信是否已配置"""
        wechat_config = self.get_wechat_config()
        return bool(wechat_config['appid'] and wechat_config['appsecret'])
    
    def is_gemini_configured(self) -> bool:
        """检查Gemini是否已配置"""
        gemini_config = self.get_gemini_config()
        return bool(gemini_config['api_key'])
    
    def is_deepseek_configured(self) -> bool:
        """检查DeepSeek是否已配置"""
        deepseek_config = self.get_deepseek_config()
        return bool(deepseek_config['api_key'])
    
    def is_dashscope_configured(self) -> bool:
        """检查阿里云百炼是否已配置"""
        dashscope_config = self.get_dashscope_config()
        return bool(dashscope_config['api_key'])
    
    def is_pexels_configured(self) -> bool:
        """检查Pexels是否已配置"""
        pexels_config = self.get_pexels_config()
        return bool(pexels_config['api_key'])
    
    def get_config_status(self) -> Dict[str, bool]:
        """获取配置状态"""
        return {
            'wechat_configured': self.is_wechat_configured(),
            'gemini_configured': self.is_gemini_configured(),
            'deepseek_configured': self.is_deepseek_configured(),
            'dashscope_configured': self.is_dashscope_configured(),
            'pexels_configured': self.is_pexels_configured(),
            'config_file_exists': os.path.exists(self.config_file)
        }

    def _start_token_monitor_thread(self):
        def monitor():
            while True:
                try:
                    config = self.load_config()
                    access_token = config.get('wechat_access_token', '')
                    expire_time = int(config.get('wechat_access_token_expire_time', 0))
                    now = int(time.time())
                    remain = expire_time - now if expire_time else None
                    try:
                        now_str = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        now_str = str(now)
                    try:
                        expire_str = datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S') if expire_time else '无'
                    except Exception:
                        expire_str = str(expire_time)
                    # logger.info(f"access_token检查: 当前时间{now_str}, 过期时间{expire_str}, 剩余{remain}秒")
                    # 如果token快到期（2分钟内）或已过期/不存在，则刷新
                    if (access_token and expire_time and remain <= 120) or (not access_token or not expire_time or remain <= 0):
                        logger.info("access_token即将过期或已过期，自动刷新...")
                        wechat_config = self.get_wechat_config()
                        if wechat_config.get('appid') and wechat_config.get('appsecret'):
                            try:
                                from services.wechat_service import WeChatService
                                ws = WeChatService()
                                token_info = ws.get_access_token(
                                    wechat_config['appid'],
                                    wechat_config['appsecret']
                                )
                                if token_info and token_info.get('access_token'):
                                    self.save_config({
                                        'wechat_access_token': token_info['access_token'],
                                        'wechat_access_token_expires_in': token_info['expires_in'],
                                        'wechat_access_token_expire_time': token_info['expire_time'],
                                        'wechat_access_token_expire_time_str': token_info['expire_time_str'],
                                        'wechat_access_token_update_time': token_info['update_time']
                                    })
                                    logger.info("access_token自动刷新成功")
                                else:
                                    logger.warning("自动刷新access_token失败")
                            except Exception as e:
                                logger.error(f"自动刷新access_token时异常: {str(e)}")
                        else:
                            logger.warning("未配置appid/appsecret，无法自动刷新access_token")
                    # 每30秒检查一次
                    time.sleep(30)
                except Exception as e:
                    logger.error(f"access_token自动刷新线程异常: {str(e)}")
=======
"""
配置服务模块
处理应用配置的加载、保存和验证
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import threading
import time

logger = logging.getLogger(__name__)

class ConfigService:
    """配置服务类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        self._start_token_monitor_thread()
        logger.info(f"配置服务初始化完成，配置文件: {self.config_file}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "wechat_appid": "",
            "wechat_appsecret": "",
            "gemini_api_key": "",
            "gemini_model": "gemini-2.5-flash",
            "deepseek_api_key": "",
            "deepseek_model": "deepseek-chat",
            "dashscope_api_key": "",
            "dashscope_model": "qwen-turbo",
            "pexels_api_key": "",
            "coze_token": "",  # 新增coze令牌
            "image_model": "gemini",  # 默认生图模型
            "author": "AI笔记",
            "content_source_url": "",
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("从文件加载配置成功")
                    
                # 合并默认配置，确保所有必要字段存在
                merged_config = self.default_config.copy()
                merged_config.update(config)
                
                return merged_config
            else:
                logger.info("配置文件不存在，使用默认配置")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"加载配置时发生错误: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 验证配置数据
            if not self._validate_config(config_data):
                logger.error("配置数据验证失败")
                return False
            
            # 加载现有配置
            current_config = self.load_config()
            
            # 更新配置
            current_config.update(config_data)
            current_config["updated_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果是首次创建，设置创建时间
            if not os.path.exists(self.config_file):
                current_config["created_at"] = current_config["updated_at"]
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, ensure_ascii=False, indent=4)
            
            logger.info("配置保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存配置时发生错误: {str(e)}")
            return False
    
    def _validate_config(self, config_data: Dict[str, Any]) -> bool:
        """验证配置数据"""
        required_fields = ['wechat_appid', 'wechat_appsecret', 'gemini_api_key']
        
        for field in required_fields:
            if field in config_data:
                value = config_data[field]
                if not isinstance(value, str) or not value.strip():
                    logger.error(f"必填字段 {field} 不能为空")
                    return False
        
        # 验证模型名称
        if 'gemini_model' in config_data:
            valid_models = ['gemini-2.5-flash', 'gemini-2.5-pro']
            if config_data['gemini_model'] not in valid_models:
                logger.warning(f"未知的Gemini模型: {config_data['gemini_model']}")
        
        return True
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取单个配置值"""
        try:
            config = self.load_config()
            return config.get(key, default)
        except Exception as e:
            logger.error(f"获取配置值时发生错误: {str(e)}")
            return default
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """设置单个配置值"""
        try:
            config = self.load_config()
            config[key] = value
            return self.save_config(config)
        except Exception as e:
            logger.error(f"设置配置值时发生错误: {str(e)}")
            return False
    
    def get_wechat_config(self) -> Dict[str, str]:
        """获取微信配置"""
        config = self.load_config()
        return {
            'appid': config.get('wechat_appid', ''),
            'appsecret': config.get('wechat_appsecret', '')
        }
    
    def get_gemini_config(self) -> Dict[str, str]:
        """获取Gemini配置"""
        config = self.load_config()
        return {
            'api_key': config.get('gemini_api_key', ''),
            'model': config.get('gemini_model', 'gemini-2.5-flash')
        }
    
    def get_deepseek_config(self) -> Dict[str, str]:
        """获取DeepSeek配置"""
        config = self.load_config()
        return {
            'api_key': config.get('deepseek_api_key', ''),
            'model': config.get('deepseek_model', 'deepseek-chat')
        }
    
    def get_dashscope_config(self) -> Dict[str, str]:
        """获取阿里云百炼配置"""
        config = self.load_config()
        return {
            'api_key': config.get('dashscope_api_key', ''),
            'model': config.get('dashscope_model', 'qwen-turbo')
        }
    
    def get_pexels_config(self) -> Dict[str, str]:
        """获取Pexels配置"""
        config = self.load_config()
        return {
            'api_key': config.get('pexels_api_key', '')
        }
    
    def get_coze_config(self) -> Dict[str, str]:
        """获取Coze配置"""
        config = self.load_config()
        return {
            'coze_token': config.get('coze_token', ''),
            'coze_workflow_id': config.get('coze_workflow_id', '')
        }
    
    def get_author_config(self) -> Dict[str, str]:
        """获取作者配置"""
        config = self.load_config()
        return {
            'author': config.get('author', 'AI笔记'),
            'content_source_url': config.get('content_source_url', '')
        }
    
    def is_wechat_configured(self) -> bool:
        """检查微信是否已配置"""
        wechat_config = self.get_wechat_config()
        return bool(wechat_config['appid'] and wechat_config['appsecret'])
    
    def is_gemini_configured(self) -> bool:
        """检查Gemini是否已配置"""
        gemini_config = self.get_gemini_config()
        return bool(gemini_config['api_key'])
    
    def is_deepseek_configured(self) -> bool:
        """检查DeepSeek是否已配置"""
        deepseek_config = self.get_deepseek_config()
        return bool(deepseek_config['api_key'])
    
    def is_dashscope_configured(self) -> bool:
        """检查阿里云百炼是否已配置"""
        dashscope_config = self.get_dashscope_config()
        return bool(dashscope_config['api_key'])
    
    def is_pexels_configured(self) -> bool:
        """检查Pexels是否已配置"""
        pexels_config = self.get_pexels_config()
        return bool(pexels_config['api_key'])
    
    def get_config_status(self) -> Dict[str, bool]:
        """获取配置状态"""
        return {
            'wechat_configured': self.is_wechat_configured(),
            'gemini_configured': self.is_gemini_configured(),
            'deepseek_configured': self.is_deepseek_configured(),
            'dashscope_configured': self.is_dashscope_configured(),
            'pexels_configured': self.is_pexels_configured(),
            'config_file_exists': os.path.exists(self.config_file)
        }

    def _start_token_monitor_thread(self):
        def monitor():
            while True:
                try:
                    config = self.load_config()
                    access_token = config.get('wechat_access_token', '')
                    expire_time = int(config.get('wechat_access_token_expire_time', 0))
                    now = int(time.time())
                    remain = expire_time - now if expire_time else None
                    try:
                        now_str = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        now_str = str(now)
                    try:
                        expire_str = datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S') if expire_time else '无'
                    except Exception:
                        expire_str = str(expire_time)
                    # logger.info(f"access_token检查: 当前时间{now_str}, 过期时间{expire_str}, 剩余{remain}秒")
                    # 如果token快到期（2分钟内）或已过期/不存在，则刷新
                    if (access_token and expire_time and remain <= 120) or (not access_token or not expire_time or remain <= 0):
                        logger.info("access_token即将过期或已过期，自动刷新...")
                        wechat_config = self.get_wechat_config()
                        if wechat_config.get('appid') and wechat_config.get('appsecret'):
                            try:
                                from services.wechat_service import WeChatService
                                ws = WeChatService()
                                token_info = ws.get_access_token(
                                    wechat_config['appid'],
                                    wechat_config['appsecret']
                                )
                                if token_info and token_info.get('access_token'):
                                    self.save_config({
                                        'wechat_access_token': token_info['access_token'],
                                        'wechat_access_token_expires_in': token_info['expires_in'],
                                        'wechat_access_token_expire_time': token_info['expire_time'],
                                        'wechat_access_token_expire_time_str': token_info['expire_time_str'],
                                        'wechat_access_token_update_time': token_info['update_time']
                                    })
                                    logger.info("access_token自动刷新成功")
                                else:
                                    logger.warning("自动刷新access_token失败")
                            except Exception as e:
                                logger.error(f"自动刷新access_token时异常: {str(e)}")
                        else:
                            logger.warning("未配置appid/appsecret，无法自动刷新access_token")
                    # 每30秒检查一次
                    time.sleep(30)
                except Exception as e:
                    logger.error(f"access_token自动刷新线程异常: {str(e)}")
>>>>>>> 4939a71745bd4c2b6983a54b58451f6e8eb98712
                    time.sleep(60)