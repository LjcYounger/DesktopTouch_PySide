import numpy as np
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt

from constants import RingConstants, GlobalConstants
from img_utils import change_image_by_grayscale

class Ring:
    """触摸圆环特效类
    
    创建一个随时间变化的圆形扩散特效，包含颜色渐变、透明度变化和尺寸缩放效果。
    使用constants中的插值函数和常量来实现平滑的动画效果。
    """
    START_ROTATION = RingConstants.get_start_rotation()

    @staticmethod
    def get_frame(time) -> QPixmap | None:
        """
        根据时间百分比生成当前帧的QPixmap
        """
        time_percentage = time / RingConstants.START_LIFETIME
        # 限制时间范围在0-1之间
        if time_percentage < 0.0 or time_percentage > 1.0:
            return None
        
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
        actual_size = max(1, int(GlobalConstants.SIZE * RingConstants.START_SIZE * size_multiplier))  # 确保至少为1像素
        
        # 应用颜色和透明度变换
        result_pixmap = change_image_by_grayscale(
            RingConstants.GRAYSCALE_IMAGE,
            rgb_values,
            alpha_value
        )
        
        # 缩放基础图案
        scaled_pixmap = result_pixmap.scaled(
            actual_size, actual_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )

        return scaled_pixmap

    @staticmethod
    def draw_centered_pixmap(painter: QPainter, pixmap: QPixmap, target_rect):
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