import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal, QObject
from pynput import mouse

from constants import GlobalConstants
from utils import set_mouse_thru, get_fps

from components.touch_effect_widget import TouchEffectWidget
from components.full_screen_widget import FullScreenWidget

class MouseSignalHandler(QObject):
    """鼠标事件信号处理器"""
    mouse_clicked = Signal(QPoint)
    mouse_moved = Signal(QPoint, bool)  # pos, is_pressed
    mouse_state_changed = Signal(bool)  # is_pressed
    
    def __init__(self):
        super().__init__()

class TransparentWindow(QMainWindow):
    # 定义更新画面信号
    update_signal = Signal(float)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_mouse_handler()
        self.start_mouse_listener()
        self.setup_timer()
        self.touch_effects = []  # 存储所有触摸效果widget
        self.is_mouse_pressed = False  # 当前鼠标按下状态
        
        # 创建全屏特效控件
        self.setup_fullscreen_effects()
        
        #self.fps = get_fps()

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
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)

    def setup_fullscreen_effects(self):
        """设置全屏特效控件"""
        screens = QApplication.screens()
        
        # 创建统一的全屏特效控件
        self.fullscreen_widget = FullScreenWidget(self.update_signal, self)
        self.fullscreen_widget.set_fullscreen_geometry(screens)
        self.fullscreen_widget.show()

    def setup_mouse_handler(self):
        """设置鼠标事件处理器"""
        self.mouse_handler = MouseSignalHandler()
        self.mouse_handler.mouse_clicked.connect(self.handle_mouse_click)
        self.mouse_handler.mouse_moved.connect(self.handle_mouse_move)
        self.mouse_handler.mouse_state_changed.connect(self.handle_mouse_state)

    def handle_mouse_click(self, global_pos):
        """处理鼠标点击事件"""
        local_pos = self.mapFromGlobal(global_pos)
        self.create_touch_effect(local_pos)

    def handle_mouse_move(self, global_pos, is_pressed):
        """处理鼠标移动事件 - 传递给全屏特效"""
        local_pos = self.mapFromGlobal(global_pos)
        self.fullscreen_widget.add_trail_input(local_pos, is_pressed)

    def handle_mouse_state(self, is_pressed):
        """处理鼠标按键状态变化"""
        self.is_mouse_pressed = is_pressed

    def setup_timer(self):
        """设置60帧计时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_timeout)
        self.frame_time = 1000.0 / GlobalConstants.MAX_FPS
        self.timer.start(self.frame_time)
        self.elapsed_time = 0.0

    def on_timer_timeout(self):
        """计时器超时处理"""
        current_time = time.time()
        
        # 发送更新信号（会触发全屏特效更新）
        self.update_signal.emit(current_time)
        
        # 清理已经完成的特效
        self.touch_effects = [effect for effect in self.touch_effects if effect.isVisible()]

    def start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if button in GlobalConstants.MOUSE_HIT_AREA:
                if pressed:
                    self.mouse_handler.mouse_clicked.emit(QPoint(x, y))
                # 发送状态变化信号
                self.mouse_handler.mouse_state_changed.emit(pressed)

        def on_move(x, y):
            # 使用当前鼠标状态
            self.mouse_handler.mouse_moved.emit(QPoint(x, y), self.is_mouse_pressed)

        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
        self.mouse_listener.start()

    def create_touch_effect(self, pos):
        """在指定位置创建触摸效果"""
        effect_widget = TouchEffectWidget(pos, time.time(), self.update_signal, self)
        side = GlobalConstants.TOUCH_EFFECT_WIDGET_SIDE
        effect_widget.setGeometry(pos.x() - side / 2, pos.y() - side / 2, side, side)
        effect_widget.show()
        self.touch_effects.append(effect_widget)

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