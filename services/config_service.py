"""
配置服务模块
处理应用配置的加载、保存和验证
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigService:
    """配置服务类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        logger.info(f"配置服务初始化完成，配置文件: {self.config_file}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "wechat_appid": "",
            "wechat_appsecret": "",
            "gemini_api_key": "",
            "gemini_model": "gemini-2.5-flash",
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
    
    def get_config_status(self) -> Dict[str, bool]:
        """获取配置状态"""
        return {
            'wechat_configured': self.is_wechat_configured(),
            'gemini_configured': self.is_gemini_configured(),
            'config_file_exists': os.path.exists(self.config_file)
        }