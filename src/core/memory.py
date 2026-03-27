"""记忆系统"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class Memory:
    """Agent记忆管理"""
    
    def __init__(self):
        self.short_term: List[Dict[str, Any]] = []
        self.long_term: Dict[str, Any] = {}
    
    def add_short_term(self, content: str, metadata: Optional[Dict] = None):
        """添加短期记忆"""
        self.short_term.append({
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
    
    def add_long_term(self, key: str, value: Any):
        """添加长期记忆"""
        self.long_term[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent(self, n: int = 5) -> List[Dict]:
        """获取最近的n条短期记忆"""
        return self.short_term[-n:]
    
    def get_long_term(self, key: str) -> Optional[Any]:
        """获取长期记忆"""
        if key in self.long_term:
            return self.long_term[key]["value"]
        return None
