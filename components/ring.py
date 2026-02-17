import numpy as np
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt

from constants import RingConstants
from img_utils import change_image_by_grayscale

class Ring:
    """触摸圆环特效类
    
    创建一个随时间变化的圆形扩散特效，包含颜色渐变、透明度变化和尺寸缩放效果。
    使用constants中的插值函数和常量来实现平滑的动画效果。
    """
    
    def __init__(self, speed=1.0, size=100, pattern=None, position=(0, 0)):
        """
        初始化圆环特效
        
        Args:
            speed (float): 动画播放速度倍数
            size (int): 基准尺寸大小
            pattern (QImage): 基础灰度图案
            position (tuple): 初始位置坐标 (x, y)
        """
        self.speed = speed
        self.size = size
        self.position = position
        self.pattern = pattern or RingConstants.GRAYSCALE_IMAGE
        self.start_rotation = RingConstants.get_start_rotation()
        
        # 计算时间增量
        self.time_delta = 1.0 / (RingConstants.START_LIFETIME * speed)
        self.current_time = 0.0
        
    def get_frame(self, time_percentage):
        """
        根据时间百分比生成当前帧的QPixmap
        
        Args:
            time_percentage (float): 时间进度百分比 (0.0-1.0)
            
        Returns:
            QPixmap: 当前帧的图像
        """
        # 限制时间范围在0-1之间
        time_percentage = max(0.0, min(1.0, time_percentage))
        self.current_time = time_percentage
        
        # 使用推导式一次性计算RGB颜色值
        rgb_values = tuple(
            int(max(0, min(255, RingConstants.COLOR_OVER_LIFETIME[i](time_percentage))))
            for i in range(3)  # r, g, b三个通道
        )
        
        # 获取alpha值
        alpha_value = int(max(0, min(255, RingConstants.COLOR_OVER_LIFETIME[3](time_percentage))))
        
        # 计算尺寸缩放因子
        size_multiplier = float(RingConstants.SIZE_OVER_LIFETIME(time_percentage))
        
        # 计算实际尺寸
        actual_size = int(self.size * size_multiplier * RingConstants.START_SIZE)
        actual_size = max(1, actual_size)  # 确保至少为1像素
        
        # 缩放基础图案
        scaled_pattern = self.pattern.scaled(
            actual_size, actual_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 应用颜色和透明度变换
        result_pixmap = change_image_by_grayscale(
            scaled_pattern,
            rgb_values,
            alpha_value
        )
        
        return result_pixmap
    
    def is_alive(self):
        """检查特效是否仍然存活"""
        return self.current_time <= 1.0
    
    def reset(self):
        """重置特效状态"""
        self.current_time = 0.0