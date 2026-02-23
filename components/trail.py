import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QPixmap, QTransform

from constants import TrailConstants
from img_utils import change_image_by_grayscale, repeat_vertical_strip_horizontally

from constants import TrailConstants

@dataclass
class TrailPoint:
    """拖尾点数据结构"""
    position: QPointF
    timestamp: float

@dataclass
class TrailSegment:
    """拖尾线段数据结构"""
    start_point: TrailPoint
    end_point: TrailPoint
    width: float
    color: tuple
    age_ratio: float
    length: float  # 添加线段长度
    angle: float   # 添加线段倾斜角(弧度)

class TrailRenderer:
    """拖尾渲染器 - 专门负责生成拖尾绘制数据"""
    constants = TrailConstants()
    def __init__(self):
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
        
    def add_point(self, position: QPointF, timestamp: float):
        """添加拖尾点"""
        point = TrailPoint(position, timestamp)
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
            
            # 计算线段长度和角度
            dx = end_point.position.x() - start_point.position.x()
            dy = end_point.position.y() - start_point.position.y()
            length = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx)  # 弧度制角度
            
            segment = TrailSegment(
                start_point=start_point,
                end_point=end_point,
                width=self.constants.WIDTH(age_ratio),
                color=self.constants.get_color(age_ratio),
                age_ratio=age_ratio,
                length=length,
                angle=angle
            )
            segments.append(segment)
            
        return segments

    def draw_segments(self, painter: QPainter, segments: List[TrailSegment]):
        """绘制拖尾线段 - 修复QPainter资源管理问题"""
        if not segments:
            return
            
        # 保存当前painter状态
        painter.save()
        
        try:
            for segment in segments:
                grayscale_image_slice_index = int(segment.age_ratio * len(self.constants.GARYSCALE_IMAGE_SLICES))
                grayscale_image_slice = self.constants.GARYSCALE_IMAGE_SLICES[grayscale_image_slice_index].scaled(1, segment.width)

                # 获取线段的起始点和结束点
                start_pos = segment.start_point.position
                end_pos = segment.end_point.position
                
                # 直接使用预计算的长度和角度
                length = segment.length
                angle_degrees = math.degrees(segment.angle)  # 转换为角度制用于旋转

                rendered_image_slice = change_image_by_grayscale(grayscale_image_slice, segment.color[:-1], segment.color[-1])
                rendered_image_slice = rendered_image_slice.transformed(QTransform().rotate(angle_degrees))
                
                # 计算单位向量
                if length == 0:
                    continue
                    
                unit_dx = math.cos(segment.angle)
                unit_dy = math.sin(segment.angle)
                
                # 逐个绘制切片
                for i in range(int(length)):
                    # 计算当前切片中心点的位置
                    progress = (i + 0.5) / length  # 中心点位置
                    center_x = start_pos.x() + progress * (end_pos.x() - start_pos.x())
                    center_y = start_pos.y() + progress * (end_pos.y() - start_pos.y())
                    
                    # 计算切片左上角坐标（考虑切片宽度的一半偏移）
                    half_width = 1 / 2.0
                    corner_x = center_x - unit_dx * half_width
                    corner_y = center_y - unit_dy * half_width
                    
                    # 在计算出的确切位置绘制切片
                    painter.drawPixmap(corner_x, corner_y, rendered_image_slice)
                    
        finally:
            # 恢复painter状态
            painter.restore()