import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QMouseEvent, QScreen, QPainter, QColor, QPen, QShowEvent
from PySide6.QtWidgets import QWidget
from pynput import mouse

from constants import GlobalConstants
from utils import set_mouse_thru

class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.click_points = []  # 存储点击位置
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # 设置鼠标穿透
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置画笔和画刷
        pen = QPen(QColor(255, 0, 0, 200), 3)  # 红色边框，半透明
        painter.setPen(pen)
        painter.setBrush(QColor(255, 0, 0, 100))  # 红色填充，更透明
        
        # 绘制所有点击点的圆圈
        for point in self.click_points:
            painter.drawEllipse(point, 100, 100)  # 以点击点为中心，100像素半径画圆
            
    def add_point(self, point):
        self.click_points.append(point)
        self.update()

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_mouse_listener()

    def initUI(self):
        # 设置窗口无边框
        self.setWindowFlags(Qt.FramelessWindowHint | 
                            Qt.WindowStaysOnTopHint | 
                            Qt.Tool | 
                            Qt.WindowDoesNotAcceptFocus)
        
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取所有屏幕信息
        screens = QApplication.screens()
        
        # 计算所有屏幕合起来的最大尺寸
        total_rect = QRect()
        for screen in screens:
            total_rect = total_rect.united(screen.geometry())
        
        # 设置窗口大小为所有屏幕合起来的尺寸
        self.setGeometry(total_rect)
        
        # 创建并添加绘图控件
        self.drawing_widget = DrawingWidget(self)
        self.drawing_widget.setGeometry(total_rect)
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)


    def start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if pressed and button in GlobalConstants.MOUSE_HIT_AREA:
                # 将屏幕坐标转换为窗口坐标
                local_pos = self.mapFromGlobal(QPoint(x, y))
                self.drawing_widget.add_point(local_pos)

        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

    def showEvent(self, event):
        """窗口显示时设置Windows穿透属性"""
        super().showEvent(event)
        hwnd = int(self.winId())
        set_mouse_thru(hwnd)

def main():
    app = QApplication(sys.argv)
    
    # 创建并显示透明窗口
    window = TransparentWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
