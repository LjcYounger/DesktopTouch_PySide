from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, Signal

from components.ring import Ring
from components.ring_3 import Ring3

class TouchEffectWidget(QWidget):
    """基于优化后Ring类的特效widget"""
    
    def __init__(self, mouse_pos: tuple, initial_time: float, update_signal: Signal, parent=None):
        super().__init__(parent)
        self.center_pos = mouse_pos
        self.initial_time = initial_time
        self.ring_pixmap = None  # 初始化pixmap属性
        self.ring_3_pixmap = None
        
        self.ring = Ring()
        self.ring_3 = Ring3()
        # 连接更新信号
        update_signal.connect(self.update_effect)
        
        # 设置widget属性
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.setWindowFlags(Qt.Widget)

        
    def update_effect(self, current_time) -> bool:
        """更新特效动画"""
        self.time = current_time - self.initial_time
        self.ring_pixmap = self.ring.get_frame(self.time)
        self.ring_3_pixmap = self.ring_3.get_frame(self.time)

        if all((self.ring_pixmap, self.ring_3_pixmap)) is None:
            self.hide()  # 隐藏而不是删除，让父窗口的清理逻辑处理
            return False
        self.update()  # 触发重绘
        return True
            
    def paintEvent(self, event):
        """绘制特效帧"""
            
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            # 使用Ring类的静态绘制函数
            if self.ring_pixmap:
                self.ring.draw_centered_pixmap(painter, self.ring_pixmap, self.rect())
            if self.ring_3_pixmap:
                self.ring_3.draw_centered_pixmap(painter, self.ring_3_pixmap, self.rect())
        finally:
            # QPainter会自动清理，不需要手动调用end()
            pass