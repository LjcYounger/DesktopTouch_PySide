import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap
from PySide6.QtCore import Qt, QRect

class PainterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 QPainter 演示")
        self.setGeometry(100, 100, 500, 400)
        
        # 添加加载图片按钮
        self.load_button = QPushButton("加载图片")
        self.load_button.clicked.connect(self.load_image)
        self.image = None
        
        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addStretch()
        self.setLayout(layout)
    
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.bmp *.gif)"
        )
        if file_name:
            self.image = QPixmap(file_name)
            self.update()  # 触发重绘
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制矩形
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        brush = QBrush(Qt.blue)
        painter.setBrush(brush)
        painter.drawRect(50, 50, 100, 80)
        
        # 绘制圆形
        pen.setColor(Qt.red)
        painter.setPen(pen)
        brush.setColor(Qt.yellow)
        painter.setBrush(brush)
        painter.drawEllipse(200, 50, 80, 80)
        
        # 绘制线条
        pen.setColor(Qt.green)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(50, 180, 300, 180)
        
        # 绘制文字
        painter.setPen(Qt.black)
        painter.setFont(self.font())
        painter.drawText(50, 220, "Hello PySide6 QPainter!")
        
        # 绘制图片（如果已加载）
        if self.image:
            # 在指定位置绘制图片
            painter.drawPixmap(350, 50, self.image.scaled(10000, 10000, Qt.KeepAspectRatio))
            
            # 绘制带透明度的图片
            painter.setOpacity(0.7)
            painter.drawPixmap(350, 180, self.image.scaled(80, 80, Qt.KeepAspectRatio))
            painter.setOpacity(1.0)  # 恢复不透明度

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = PainterWidget()
    widget.show()
    sys.exit(app.exec())