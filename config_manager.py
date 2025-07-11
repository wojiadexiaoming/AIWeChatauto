import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "wechat_appid": "",
            "wechat_appsecret": "",
            "gemini_api_key": "",
            "gemini_model": "gemini-2.5-flash",
            "author": "AI笔记",
            "content_source_url": "",
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 合并默认配置，确保所有必要字段存在
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                
                logger.info("配置加载成功")
                return config
            else:
                logger.info("配置文件不存在，使用默认配置")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"加载配置时发生错误: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config_data):
        """保存配置"""
        try:
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
    
    def get_config_value(self, key, default=None):
        """获取单个配置值"""
        try:
            config = self.load_config()
            return config.get(key, default)
        except:
            return default
    
    def set_config_value(self, key, value):
        """设置单个配置值"""
        try:
            config = self.load_config()
            config[key] = value
            return self.save_config(config)
        except:
            return False
