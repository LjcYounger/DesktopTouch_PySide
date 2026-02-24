import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLFramebufferObjectFormat, QOpenGLWindow
from PySide6.QtCore import Qt, QTimer
import moderngl
import math
from PIL import Image

class CircularImageViewer(QOpenGLWindow):
    def __init__(self, image_path=None):
        super().__init__()
        self.resize(400, 400)
        
        # 从文件加载图像或创建示例图像
        if image_path:
            self.load_image_from_file(image_path)
        else:
            self.create_sample_image()
        
        # 初始化OpenGL相关变量
        self.ctx = None
        self.program = None
        self.vao = None
        self.texture = None
        
        # 定时器用于刷新画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # 约60FPS
    
    def load_image_from_file(self, image_path):
        """从文件加载图像并转换为灰度图"""
        try:
            # 加载图像
            img = Image.open(image_path).convert('L')  # 直接转换为灰度
            self.image_data = np.array(img)
            self.img_width, self.img_height = img.size
            
            print(f"成功加载并处理图像: {image_path}")
            print(f"尺寸: {self.img_width}x{self.img_height}")
            
        except Exception as e:
            print(f"加载图像时出错: {e}")
            self.create_sample_image()
    
    def create_sample_image(self):
        # 创建一个简单的灰度图像用于测试
        self.img_width, self.img_height = 200, 20
        self.image_data = np.zeros((self.img_height, self.img_width), dtype=np.uint8)
        
        # 创建渐变效果
        for i in range(self.img_width):
            intensity = int(255 * (i / self.img_width))
            self.image_data[:, i] = intensity
    
    def initializeGL(self):
        # 初始化ModernGL上下文
        self.ctx = moderngl.create_context()
        
        # 顶点着色器
        vertex_shader = '''
        #version 330
        in vec2 in_position;
        in vec2 in_texcoord;
        out vec2 v_texcoord;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
            v_texcoord = in_texcoord;
        }
        '''
        
        # 片段着色器
        fragment_shader = '''
        #version 330
        uniform sampler2D texture0;
        uniform float outer_radius;
        uniform float inner_radius;
        uniform vec2 center;
        uniform vec2 screen_size;
        uniform int img_width;
        uniform int img_height;
        
        in vec2 v_texcoord;
        out vec4 fragColor;
        
        void main() {
            vec2 coord = gl_FragCoord.xy;
            vec2 normalized_coord = (coord - center) / screen_size.y * 2.0;
            
            float distance = length(normalized_coord);
            
            if (distance > outer_radius || distance < inner_radius) {
                discard;
            }
            
            // 计算角度
            float angle = atan(normalized_coord.y, normalized_coord.x);
            float normalized_angle = (angle + 3.14159) / (2.0 * 3.14159);
            
            // 计算半径映射
            float radius_ratio = (distance - inner_radius) / (outer_radius - inner_radius);
            
            // 采样纹理
            vec2 tex_coord = vec2(normalized_angle, radius_ratio);
            vec4 tex_color = texture(texture0, tex_coord);
            
            fragColor = tex_color;
        }
        '''
        
        # 创建着色器程序
        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
        # 创建顶点数据（全屏四边形）
        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,  # 左下
             1.0, -1.0, 1.0, 0.0,  # 右下
            -1.0,  1.0, 0.0, 1.0,  # 左上
             1.0,  1.0, 1.0, 1.0   # 右上
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # 创建纹理
        self.texture = self.ctx.texture(
            (self.img_width, self.img_height),
            1,  # 单通道
            self.image_data.tobytes(),
            dtype='f1'
        )
        self.texture.use(0)
        
        # 设置uniform变量
        self.program['texture0'] = 0
        self.program['img_width'] = self.img_width
        self.program['img_height'] = self.img_height
    
    def paintGL(self):
        if not self.ctx:
            return
            
        # 清除屏幕
        self.ctx.clear(0.2, 0.2, 0.2, 1.0)
        
        # 更新uniform变量
        screen_width, screen_height = self.size().width(), self.size().height()
        center_x, center_y = screen_width / 2, screen_height / 2
        outer_radius = min(center_x, center_y) / screen_height * 0.8
        inner_radius = outer_radius - 0.15
        
        self.program['center'] = (center_x, center_y)
        self.program['screen_size'] = (screen_width, screen_height)
        self.program['outer_radius'] = outer_radius
        self.program['inner_radius'] = inner_radius
        
        # 绘制
        self.vao.render(moderngl.TRIANGLE_STRIP)
    
    def resizeGL(self, width, height):
        if self.ctx:
            self.ctx.viewport = (0, 0, width, height)
    
    def closeEvent(self, event):
        # 清理资源
        if self.texture:
            self.texture.release()
        if self.vbo:
            self.vbo.release()
        if self.vao:
            self.vao.release()
        if self.program:
            self.program.release()
        if self.ctx:
            self.ctx.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # 设置OpenGL格式
    format = QSurfaceFormat()
    format.setVersion(3, 3)
    format.setProfile(QSurfaceFormat.CoreProfile)
    format.setSamples(4)  # 抗锯齿
    QSurfaceFormat.setDefaultFormat(format)
    
    # 检查是否有命令行参数指定图像文件
    image_path = None
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # 如果没有命令行参数，打开文件对话框选择图像
        image_path, _ = QFileDialog.getOpenFileName(
            None, 
            "选择图像文件", 
            "", 
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
    
    window = CircularImageViewer(image_path)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()