import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QPixmap, QTransform

from constants import TrailConstants, GlobalConstants
from img_utils import change_image_by_grayscale

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

class TrailRenderer:
    """拖尾渲染器 - 专门负责生成拖尾绘制数据"""
    constants = TrailConstants()
    def __init__(self):
        # 拖尾点存储
        self.points: List[TrailPoint] = []
        self.is_drawing = False
        self.last_update_time = 0.0    # 记录上次更新时间
        # 添加缓存列表，格式：List[Dict{end_point的时间戳：Dict{线段长度：线段长度，线段倾斜角：线段倾斜角，切片坐标：切片坐标}}]
        self.segments_cache: List[Dict[float, Dict[str, any]]] = []
        self.max_cache_size = math.ceil(GlobalConstants.MAX_FPS * TrailConstants.TIME)
        
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
        cutoff_time = current_time - self.constants.TIME

        # 使用列表推导式高效过滤（保留时间戳大于等于cutoff_time的点）
        self.points = [p for p in self.points if p.timestamp >= cutoff_time]
        #print(cutoff_time, [self.points[i].timestamp for i in range(len(self.points))])
        
        # 清理过期的缓存数据
        self.segments_cache = [cache for cache in self.segments_cache 
                              if list(cache.keys())[0] >= cutoff_time]
        
    def generate_segments(self) -> List[TrailSegment]:
        """每帧更新 - 生成拖尾线段数据用于绘制"""
        if len(self.points) < 2:
            return []
            
        segments = []
        current_time = self.last_update_time  # 使用记录的时间
        
        # 检查是否有可用的缓存数据
        cached_data = None
        for cache in self.segments_cache:
            if list(cache.keys())[0] == self.points[-1].timestamp:
                cached_data = cache[self.points[-1].timestamp]
                break
        
        for i in range(len(self.points) - 1):
            start_point = self.points[i]
            end_point = self.points[i + 1]
            
            # 计算线段属性
            age_ratio = (current_time - start_point.timestamp) / self.constants.TIME
            alpha = int(255 * (1 - age_ratio))  # 年龄越大越透明
            
            width = self.constants.WIDTH(age_ratio)
            
            # 如果有缓存数据则直接使用，否则重新计算
            if cached_data and i < len(cached_data.get('segments', [])):
                segment_data = cached_data['segments'][i]
                length = segment_data['length']
                angle = segment_data['angle']
                slices = segment_data['slices']
            else:
                # 计算线段长度和角度
                dx = end_point.position.x() - start_point.position.x()
                dy = end_point.position.y() - start_point.position.y()
                length = math.sqrt(dx * dx + dy * dy)
                angle = math.atan2(dy, dx)  # 弧度制角度
                
                # 预生成切片
                slices = self._generate_slices(start_point.position, end_point.position, length, angle, age_ratio, width)
                
                # 缓存新计算的数据
                if not cached_data:
                    cached_data = {'segments': []}
                    self.segments_cache.append({end_point.timestamp: cached_data})
                
                # 限制缓存大小
                if len(self.segments_cache) > self.max_cache_size:
                    self.segments_cache.pop(0)
                    
                cached_data['segments'].append({
                    'length': length,
                    'angle': angle,
                    'slices': slices
                })
            
            segment = TrailSegment(
                start_point=start_point,
                end_point=end_point,
                width=width,
                color=self.constants.get_color(age_ratio),
                age_ratio=age_ratio,
            )
            segments.append(segment)
            
        return segments
    
    def _generate_slices(self, start_pos: QPointF, end_pos: QPointF, length: float, angle: float, age_ratio: float, width: float) -> List[Tuple[float, float]]:
        """预生成切片数据 - 直接使用元组存储坐标位置"""
        slices = []
        
        # 计算单位向量
        if length == 0:
            return slices
            
        unit_dx = math.cos(angle)
        unit_dy = math.sin(angle)
        
        # 生成每个切片的位置坐标
        for i in range(math.ceil(length)):
            # 计算当前切片中心点的位置
            progress = (i + 0.5) / length  # 中心点位置
            center_x = start_pos.x() + progress * (end_pos.x() - start_pos.x())
            center_y = start_pos.y() + progress * (end_pos.y() - start_pos.y())
            
            # 计算切片左上角坐标
            half_width = 1 / 2.0
            corner_x = center_x - unit_dx * half_width
            corner_y = center_y - unit_dy * half_width
            
            slices.append((corner_x, corner_y))  # 直接存储为元组
            
        return slices

    def draw_segments(self, painter: QPainter, segments: List[TrailSegment]):
        """绘制拖尾线段 - 动态生成图像切片进行绘制"""
        if not segments:
            return
            
        # 保存当前painter状态
        painter.save()
        
        try:
            # 获取当前帧的缓存数据用于绘制
            current_cache = None
            if self.segments_cache:
                latest_cache = self.segments_cache[-1]
                current_cache = list(latest_cache.values())[0]
                
            for i, segment in enumerate(segments):
                # 获取当前segment的图像切片（动态生成）
                grayscale_image_slice_index = int(segment.age_ratio * len(self.constants.GARYSCALE_IMAGE_SLICES))
                grayscale_image_slice = self.constants.GARYSCALE_IMAGE_SLICES[grayscale_image_slice_index].scaled(1, segment.width)
                
                # 应用颜色和旋转
                rendered_image_slice = change_image_by_grayscale(
                    grayscale_image_slice, 
                    segment.color[:-1], 
                    segment.color[-1]
                )
                
                # 从缓存获取角度信息
                angle_degrees = 0
                slices = []
                if current_cache and i < len(current_cache.get('segments', [])):
                    segment_data = current_cache['segments'][i]
                    angle_degrees = math.degrees(segment_data['angle'])
                    slices = segment_data['slices']
                    rendered_image_slice = rendered_image_slice.transformed(QTransform().rotate(angle_degrees))
                
                # 绘制每个切片
                for corner_x, corner_y in slices:  # 直接解包元组
                    painter.drawPixmap(corner_x, corner_y, rendered_image_slice)
                    
        finally:
            # 恢复painter状态
            painter.restore()
