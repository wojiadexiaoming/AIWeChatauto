"""
历史记录服务模块
处理文章生成历史和发布历史的管理
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class HistoryService:
    """历史记录服务类"""
    
    def __init__(self):
        self.cache_dir = 'cache'
        self.history_file = 'data/history.json'
        self.publish_history_file = 'data/publish_history.json'
        self._ensure_directories()
        logger.info("历史记录服务初始化完成")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs('data', exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def add_generation_history(self, article_data: Dict[str, Any]) -> bool:
        """
        添加文章生成历史记录
        :param article_data: 文章数据
        :return: 是否添加成功
        """
        try:
            history = self._load_history()
            
            # 创建历史记录项
            history_item = {
                'id': self._generate_id(),
                'title': article_data.get('title', ''),
                'content_length': article_data.get('content_length', 0),
                'image_count': article_data.get('image_count', 0),
                'generated_at': article_data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'author': article_data.get('author', 'AI笔记'),
                'digest': article_data.get('digest', ''),
                'content_source_url': article_data.get('content_source_url', ''),
                'status': 'generated',  # generated, saved, published
                'cache_files': self._find_cache_files(article_data.get('title', '')),
                'media_id': None,
                'publish_id': None,
                'msg_data_id': None
            }
            
            # 添加到历史记录开头
            history.insert(0, history_item)
            
            # 限制历史记录数量（保留最近100条）
            if len(history) > 100:
                history = history[:100]
            
            self._save_history(history)
            logger.info(f"添加生成历史记录: {history_item['title']}")
            return True
            
        except Exception as e:
            logger.error(f"添加生成历史记录失败: {str(e)}")
            return False
    
    def update_draft_status(self, title: str, media_id: str) -> bool:
        """
        更新草稿保存状态
        :param title: 文章标题
        :param media_id: 微信草稿media_id
        :return: 是否更新成功
        """
        try:
            history = self._load_history()
            
            # 查找匹配的历史记录（按标题和时间匹配）
            for item in history:
                if item['title'] == title and item['status'] == 'generated':
                    item['status'] = 'saved'
                    item['media_id'] = media_id
                    item['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self._save_history(history)
                    logger.info(f"更新草稿状态: {title} -> media_id: {media_id}")
                    return True
            
            logger.warning(f"未找到匹配的生成历史记录: {title}")
            return False
            
        except Exception as e:
            logger.error(f"更新草稿状态失败: {str(e)}")
            return False
    
    def update_publish_status(self, media_id: str, publish_data: Dict[str, Any]) -> bool:
        """
        更新发布状态
        :param media_id: 微信草稿media_id
        :param publish_data: 发布结果数据
        :return: 是否更新成功
        """
        try:
            history = self._load_history()
            publish_history = self._load_publish_history()
            
            # 查找匹配的历史记录
            for item in history:
                if item['media_id'] == media_id and item['status'] == 'saved':
                    item['status'] = 'published'
                    item['publish_id'] = publish_data.get('publish_id')
                    item['msg_data_id'] = publish_data.get('msg_data_id')
                    item['published_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 添加到发布历史
                    publish_item = {
                        'id': self._generate_id(),
                        'title': item['title'],
                        'media_id': media_id,
                        'publish_id': publish_data.get('publish_id'),
                        'msg_data_id': publish_data.get('msg_data_id'),
                        'published_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'author': item['author'],
                        'content_length': item['content_length'],
                        'image_count': item['image_count']
                    }
                    publish_history.insert(0, publish_item)
                    
                    # 限制发布历史数量（保留最近50条）
                    if len(publish_history) > 50:
                        publish_history = publish_history[:50]
                    
                    self._save_history(history)
                    self._save_publish_history(publish_history)
                    logger.info(f"更新发布状态: media_id {media_id} -> publish_id {publish_data.get('publish_id')}")
                    return True
            
            logger.warning(f"未找到匹配的草稿记录: media_id {media_id}")
            return False
            
        except Exception as e:
            logger.error(f"更新发布状态失败: {str(e)}")
            return False
    
    def get_generation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取文章生成历史
        :param limit: 返回数量限制
        :return: 历史记录列表
        """
        try:
            history = self._load_history()
            return history[:limit]
        except Exception as e:
            logger.error(f"获取生成历史失败: {str(e)}")
            return []
    
    def get_publish_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取发布历史
        :param limit: 返回数量限制
        :return: 发布历史列表
        """
        try:
            publish_history = self._load_publish_history()
            return publish_history[:limit]
        except Exception as e:
            logger.error(f"获取发布历史失败: {str(e)}")
            return []
    
    def get_article_content(self, cache_files: List[str]) -> Optional[str]:
        """
        获取文章内容（从cache文件）
        :param cache_files: cache文件列表
        :return: 文章内容
        """
        try:
            if not cache_files:
                return None
            
            # 优先使用cleaned文件
            for file_path in cache_files:
                if 'cleaned' in file_path and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
            
            # 如果没有cleaned文件，使用raw文件
            for file_path in cache_files:
                if 'raw' in file_path and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
            
            return None
            
        except Exception as e:
            logger.error(f"获取文章内容失败: {str(e)}")
            return None
    
    def _find_cache_files(self, title: str) -> List[str]:
        """
        查找与标题相关的cache文件
        :param title: 文章标题
        :return: cache文件路径列表
        """
        try:
            if not os.path.exists(self.cache_dir):
                return []
            
            # 清理标题用于文件名匹配
            safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
            
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                if safe_title in filename and filename.endswith('.html'):
                    file_path = os.path.join(self.cache_dir, filename)
                    cache_files.append(file_path)
            
            return sorted(cache_files, reverse=True)  # 最新的文件在前
            
        except Exception as e:
            logger.error(f"查找cache文件失败: {str(e)}")
            return []
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"加载历史记录失败: {str(e)}")
            return []
    
    def _save_history(self, history: List[Dict[str, Any]]):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败: {str(e)}")
    
    def _load_publish_history(self) -> List[Dict[str, Any]]:
        """加载发布历史"""
        try:
            if os.path.exists(self.publish_history_file):
                with open(self.publish_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"加载发布历史失败: {str(e)}")
            return []
    
    def _save_publish_history(self, publish_history: List[Dict[str, Any]]):
        """保存发布历史"""
        try:
            with open(self.publish_history_file, 'w', encoding='utf-8') as f:
                json.dump(publish_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存发布历史失败: {str(e)}")
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        return datetime.now().strftime('%Y%m%d%H%M%S') + str(hash(datetime.now().timestamp()))[-6:] 