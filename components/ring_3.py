import math
import random
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import QPointF

from constants import Ring3Constants
from generate_frame import generate_animated_frame

class Ring3:
    """触摸圆环特效类"""
    constants = Ring3Constants()
    def __init__(self) -> None:
        self.constants.START_LIFETIME = self.constants.get_start_lifetime()
        self.constants.START_SPEED = self.constants.get_start_speed()
        self.constants.START_SIZE = self.constants.get_start_size()

    def get_frame(self, time) -> QPixmap | None:
        """
        根据时间生成当前帧的QPixmap
        """
        return generate_animated_frame(time, self.constants)


    def draw_centered_pixmap(self, painter: QPainter, pixmap: QPixmap, target_rect):
        """
        在目标区域内居中绘制pixmap
        
        Args:
            painter (QPainter): 绘制器对象
            pixmap (QPixmap): 要绘制的图像
            target_rect: 目标区域矩形
        """
        if pixmap.isNull():
            return
            
        pixmap_rect = pixmap.rect()
        x = (target_rect.width() - pixmap_rect.width()) // 2
        y = (target_rect.height() - pixmap_rect.height()) // 2
        
        painter.drawPixmap(x, y, pixmap)
        
    @staticmethod
    def get_random_velocity() -> tuple[float, float]:
        """
        生成随机方向的速度分量
        
        Returns:
            tuple[float, float]: (velocity_x, velocity_y) 速度分量
        """
        # 生成随机起始角度（0-360度）
        angle = random.uniform(0, 360)
        # 将角度转换为弧度
        angle_rad = math.radians(angle)
        
        # 获取起始速度
        start_speed = Ring3Constants.get_start_speed()
        
        # 计算x和y方向的速度分量
        velocity_x = start_speed * math.cos(angle_rad)
        velocity_y = start_speed * math.sin(angle_rad)
        
        return (velocity_x, velocity_y)
        
    @staticmethod
    def calculate_position(start_pos: QPointF, velocity: tuple[float, float], delta_time: float) -> QPointF:
        """
        根据起始位置、速度和时间计算当前位置
        
        Args:
            start_pos (QPointF): 起始位置
            velocity (tuple[float, float]): 速度分量 (vx, vy)
            delta_time (float): 时间增量（秒）
            
        Returns:
            QPointF: 计算后的位置
        """
        velocity_x, velocity_y = velocity
        new_x = start_pos.x() + velocity_x * delta_time
        new_y = start_pos.y() + velocity_y * delta_time
        return QPointF(new_x, new_y)