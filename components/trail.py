import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath

from constants import TrailConstants

@dataclass
class TrailPoint:
    """拖尾点数据结构"""
    position: QPointF
    timestamp: float
    pressure: float = 1.0  # 压感强度(0-1)

@dataclass
class TrailSegment:
    """拖尾线段数据结构"""
    start_point: TrailPoint
    end_point: TrailPoint
    width: float
    color: tuple
    alpha: int

class TrailRenderer:
    """拖尾渲染器 - 专门负责生成拖尾绘制数据"""
    constants = TrailConstants()
    def __init__(self):
        self.width_decay = 0.95        # 宽度衰减系数
        
        # 拖尾点存储
        self.points: List[TrailPoint] = []
        self.is_drawing = False
        self.last_update_time = 0.0    # 记录上次更新时间
        
    def start_drawing(self, position: QPointF, timestamp: float):
        """开始绘制拖尾"""
        self.is_drawing = True
        self.add_point(position, timestamp)
        
    def stop_drawing(self):
        """停止绘制拖尾"""
        self.is_drawing = False
        
    def add_point(self, position: QPointF, timestamp: float, pressure: float = 1.0):
        """添加拖尾点"""
        point = TrailPoint(position, timestamp, pressure)
        self.points.append(point)
        
        # 限制点数
        #if len(self.points) > self.max_points:
        #    self.points.pop(0)
            
    def update_frame(self, current_time: float):
        """更精确的过期点清理逻辑"""
        self.last_update_time = current_time
        
        # 计算绝对截止时间（比当前时间早lifetime秒的点需要移除）
        cutoff_time = current_time - self.constants .TIME
        
        # 使用列表推导式高效过滤（保留时间戳大于等于cutoff_time的点）
        self.points = [p for p in self.points if p.timestamp >= cutoff_time]
        #print(cutoff_time, [self.points[i].timestamp for i in range(len(self.points))])
        
    def generate_segments(self) -> List[TrailSegment]:
        """每帧更新 - 生成拖尾线段数据用于绘制"""
        if len(self.points) < 2:
            return []
            
        segments = []
        current_time = self.last_update_time  # 使用记录的时间
        
        for i in range(len(self.points) - 1):
            start_point = self.points[i]
            end_point = self.points[i + 1]
            
            # 计算线段属性
            age_ratio = (current_time - start_point.timestamp) / self.constants.TIME
            alpha = int(255 * (1 - age_ratio))  # 年龄越大越透明
            
            # 宽度根据位置递减
            width_factor = (len(self.points) - i) / len(self.points)
            width = self.constants.WIDTH(age_ratio) * width_factor * start_point.pressure
            
            segment = TrailSegment(
                start_point=start_point,
                end_point=end_point,
                width=max(1.0, width),
                color=self.constants.get_color(age_ratio),
                alpha=max(0, alpha)
            )
            segments.append(segment)
            
        return segments
    
    def get_current_position(self) -> Optional[QPointF]:
        """获取当前位置"""
        return self.points[-1].position if self.points else None
    
    def is_active(self) -> bool:
        """检查是否有活跃的拖尾"""
        return len(self.points) > 0