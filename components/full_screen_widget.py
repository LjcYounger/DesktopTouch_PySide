import time
from typing import List
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRect, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap

from .trail import TrailRenderer, TrailSegment, TrailPoint
from .ring_4 import Ring4
from constants import Ring4Constants, GlobalConstants

class FullScreenWidget(QWidget):
    """统一的全屏特效绘制控件"""
    
    def __init__(self, update_signal: Signal, parent=None):
        super().__init__(parent)
        
        # 初始化特效系统
        self.trail_renderer = TrailRenderer()
        self.ring_constants = Ring4Constants()
        self.ring_effects = []
        self.current_time = 0.0
        
        # 鼠标拖动距离追踪相关变量
        self.last_mouse_position = None
        self.accumulated_distance = 0.0
        
        # 调试用：存储所有Ring4中心点位置
        if GlobalConstants.DEBUG_MODE:
            self.ring_centers = []
        
        # 连接更新信号
        update_signal.connect(self.update_effects)
        
        # 设置widget属性
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setUpdatesEnabled(True)
        
    def update_effects(self, current_time: float):
        """更新所有特效状态"""
        self.current_time = current_time
        self.trail_renderer.update_frame(current_time)
        
        # 更新Ring特效生命周期
        self.ring_effects = [
            effect for effect in self.ring_effects 
            if current_time - effect['start_time'] < self.ring_constants.START_LIFETIME
        ]
        self.update()
        
    def add_trail_input(self, position, is_pressed: bool):
        """处理拖尾输入"""
        if is_pressed:
            if not self.trail_renderer.is_drawing:
                self.trail_renderer.start_drawing(position, self.current_time)
                # 初始化鼠标位置追踪
                self.last_mouse_position = QPointF(position)  # 确保是QPointF类型
                self.accumulated_distance = 0.0
            else:
                self.trail_renderer.add_point(position, self.current_time)
                # 计算距离并生成Ring4特效
                self._process_mouse_movement(position)
        else:
            self.trail_renderer.stop_drawing()
            # 释放鼠标时重置追踪状态
            self.last_mouse_position = None
            self.accumulated_distance = 0.0
            
    def _process_mouse_movement(self, current_position):
        """处理鼠标移动，根据累积距离生成Ring4特效"""
        if self.last_mouse_position is None:
            self.last_mouse_position = QPointF(current_position)
            return
        
        # 计算移动向量和距离
        dx = current_position.x() - self.last_mouse_position.x()
        dy = current_position.y() - self.last_mouse_position.y()
        move_distance = (dx**2 + dy**2)**0.5
        
        if move_distance == 0:
            return
            
        # 累积距离
        self.accumulated_distance += move_distance
        threshold = self.ring_constants.Emission.RATE_OVER_DISTANCE
        
        # 沿着移动路径均匀分布特效点
        while self.accumulated_distance >= threshold:
            # 计算需要回退多远来找到生成点
            backtrack_distance = self.accumulated_distance - threshold
            
            # 计算回退比例（0-1之间）
            backtrack_ratio = backtrack_distance / move_distance if move_distance > 0 else 0
            backtrack_ratio = max(0, min(1, backtrack_ratio))  # 限制在[0,1]范围内
            
            # 计算生成点位置（从当前位置往回退）
            generate_x = current_position.x() - dx * backtrack_ratio
            generate_y = current_position.y() - dy * backtrack_ratio
            generate_pos = QPointF(generate_x, generate_y)
            
            # 添加特效
            self.add_ring_at_position(generate_pos)
            
            # 减少累积距离
            self.accumulated_distance -= threshold

        # 更新最后位置
        self.last_mouse_position = current_position

    def add_ring_at_position(self, position, time_offset=0.0):
        """添加Ring特效"""
        # 确保位置是QPointF类型
        effect_pos = QPointF(position) if not isinstance(position, QPointF) else position
        
        # 为每个特效创建独立的 Ring4 实例
        ring_instance = Ring4()
        
        self.ring_effects.append({
            'position': effect_pos,
            'start_time': self.current_time + time_offset,  # 添加时间偏移
            'ring_instance': ring_instance  # 存储独立的Ring4实例
        })
        # 调试用：记录中心点位置
        if GlobalConstants.DEBUG_MODE:
            self.ring_centers.append(effect_pos)
    
    def paintEvent(self, event):
        """绘制所有特效"""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            
            # 绘制Ring特效 - 使用每个特效自己的Ring4实例
            for effect in self.ring_effects:
                elapsed = self.current_time - effect['start_time']
                # 使用该特效自己的Ring4实例
                ring = effect['ring_instance']
                frame = ring.get_frame(elapsed)
                if frame:
                    # 确保位置是QPointF类型
                    pos = QPointF(effect['position']) if not isinstance(effect['position'], QPointF) else effect['position']
                    ring.draw_centered_pixmap(painter, frame, pos, elapsed)
            
            if GlobalConstants.DEBUG_MODE:
                # 调试用：绘制永久性Ring4中心点
                painter.setPen(QPen(QColor(255, 0, 0), 3))  # 红色圆点
                painter.setBrush(QColor(255, 0, 0, 100))   # 半透明红色填充
                for center in self.ring_centers:
                    # 确保位置是QPointF类型
                    center_pos = QPointF(center) if not isinstance(center, QPointF) else center
                    painter.drawEllipse(center_pos, 5, 5)      # 绘制半径为5的圆点
            
            # 绘制拖尾特效
            segments = self.trail_renderer.generate_segments()
            for segment in segments:
                color = QColor(segment.color.red(), segment.color.green(), 
                             segment.color.blue(), segment.alpha)
                pen = QPen(color, segment.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(segment.start_point.position, segment.end_point.position)
                
        finally:
            painter.end()
    
    def set_fullscreen_geometry(self, screens):
        """设置全屏几何尺寸"""
        total_rect = QRect()
        for screen in screens:
            total_rect = total_rect.united(screen.geometry())
        self.setGeometry(total_rect)