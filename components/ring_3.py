from PySide6.QtGui import QPixmap, QPainter

from constants import Ring3Constants
from components.ring_x import RingX

class Ring3(RingX):
    """触摸圆环特效类"""
    def __init__(self) -> None:
        super().__init__(Ring3Constants())

    def draw_centered_pixmap(self, painter: QPainter, pixmap: QPixmap, target_rect, time):
        """
        在目标区域内居中绘制pixmap
        """
        if pixmap.isNull():
            return
        
        pixmap = pixmap.transformed(self.flip_transform)
            
        pixmap_rect = pixmap.rect()
        center_pos = (target_rect.width() // 2, target_rect.height() // 2)
        delta_pos = (pixmap_rect.width() // 2, pixmap_rect.height() // 2)

        for i in range(self.constants.Emission.COUNT):
            current_pos = self.calculate_current_position(center_pos, self.velocities[i], time)
            painter.drawPixmap(current_pos[0] - delta_pos[0], current_pos[1] - delta_pos[1], pixmap)