import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("鼠标穿透窗口示例")
        self.setGeometry(100, 100, 400, 300)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 无边框且置顶
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加一些控件
        label1 = QLabel("普通标签 - 会阻挡鼠标事件")
        label1.setStyleSheet("background-color: rgba(255, 0, 0, 100); padding: 10px;")
        layout.addWidget(label1)
        
        button1 = QPushButton("普通按钮 - 会阻挡鼠标事件")
        button1.setStyleSheet("background-color: rgba(0, 255, 0, 100);")
        layout.addWidget(button1)
        
        # 添加可穿透的控件
        transparent_label = QLabel("可穿透标签 - 鼠标事件会穿过")
        transparent_label.setStyleSheet("background-color: rgba(0, 0, 255, 100); padding: 10px;")
        transparent_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # 关键属性
        layout.addWidget(transparent_label)
        
        transparent_button = QPushButton("可穿透按钮 - 鼠标事件会穿过")
        transparent_button.setStyleSheet("background-color: rgba(255, 255, 0, 100);")
        transparent_button.setAttribute(Qt.WA_TransparentForMouseEvents)  # 关键属性
        layout.addWidget(transparent_button)
        
        # 连接按钮信号
        button1.clicked.connect(lambda: print("普通按钮被点击"))
        transparent_button.clicked.connect(lambda: print("这不会被触发，因为鼠标事件被穿透了"))
        
    def mousePressEvent(self, event):
        """重写鼠标按下事件来演示穿透效果"""
        print(f"窗口背景被点击，位置: {event.pos()}")
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        """绘制半透明背景以便观察效果"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(100, 100, 100, 50))  # 半透明灰色背景

class FullTransparentWindow(QMainWindow):
    """完全透明的窗口示例"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("完全透明窗口")
        self.setGeometry(600, 100, 300, 200)
        
        # 完全透明窗口设置
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 设置窗口完全透明（关键）
        self.setStyleSheet("background-color: transparent;")
        
        # 在透明窗口上添加控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 这些控件即使在透明窗口上也不会阻挡鼠标事件
        label = QLabel("透明窗口上的标签")
        label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100); padding: 10px;")
        layout.addWidget(label)
        
        button = QPushButton("透明窗口上的按钮")
        button.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        layout.addWidget(button)
        
        # 所有控件都设置为可穿透
        for widget in [label, button]:
            widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            
        button.clicked.connect(lambda: print("透明窗口按钮被点击（理论上不会触发）"))

def main():
    app = QApplication(sys.argv)
    
    # 创建两个窗口进行对比
    window1 = TransparentWindow()
    window1.show()
    
    window2 = FullTransparentWindow()
    window2.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()