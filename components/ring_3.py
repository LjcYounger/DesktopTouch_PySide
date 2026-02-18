from typing import List

from PySide6.QtGui import QPixmap, QPainter

from constants import Ring3Constants
from generate_frame import generate_animated_frame
from components.ring_x import RingX

class Ring3(RingX):
    """触摸圆环特效类"""
    def __init__(self) -> None:
        super().__init__(Ring3Constants())

    def get_frame(self, time) -> List[tuple[QPixmap, float]] | None:
        """
        根据时间生成当前帧的QPixmap
        """
        pixmap_list = []
        for i in range(self.constants.Emission.COUNT):
            # 计算每个图案的延迟时间
            delay = i * self.constants.Emission.INTERVAL
            
            # 如果当前时间还没到该图案的出现时间，则跳过
            if time < delay:
                continue
                
            # 调整时间为相对于该图案开始时间的时间
            adjusted_time = time - delay
            pixmap = generate_animated_frame(adjusted_time, self.constants)
            pixmap_list.append((pixmap, adjusted_time) if pixmap else None)
        if all(pixmap_list) is None:
            return None
        else:
            return pixmap_list
    
    def draw_centered_pixmap(self, painter: QPainter, pixmap_list: List[tuple[QPixmap, float] | None], target_rect, time):
        """
        在目标区域内居中绘制pixmap，每个图案依次间隔出现
        """
        for i, temp in enumerate(pixmap_list):
            if temp is None: continue
            pixmap, adjusted_time = temp
        
            pixmap = pixmap.transformed(self.flip_transform)
                
            pixmap_rect = pixmap.rect()
            center_pos = (target_rect.width() // 2, target_rect.height() // 2)
            delta_pos = (pixmap_rect.width() // 2, pixmap_rect.height() // 2)

            current_pos = self.calculate_current_position(center_pos, self.velocities[i], adjusted_time)
            painter.drawPixmap(current_pos[0] - delta_pos[0], current_pos[1] - delta_pos[1], pixmap)