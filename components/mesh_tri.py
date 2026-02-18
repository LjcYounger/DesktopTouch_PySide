from PySide6.QtGui import QPixmap, QPainter

from constants import MeshTriConstants
from generate_frame import generate_animated_frame
class MeshTri:
    """触摸圆环特效类
    
    创建一个随时间变化的圆形扩散特效，包含颜色渐变、透明度变化和尺寸缩放效果。
    使用constants中的插值函数和常量来实现平滑的动画效果。
    """
    constants = MeshTriConstants()
    def __init__(self) -> None:
        self.constants.START_SIZE = self.constants.get_start_size()
        self.constants.START_ROTATION = self.constants.get_start_rotation()
        self.constants.CustomData.CUSTOM1_X = self.constants.CustomData.get_custom1_x()

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