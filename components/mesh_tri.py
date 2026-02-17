import pygame as pg
import numpy as np
import random
import math

from img_utils import change_color

class MeshTri(pg.sprite.Sprite):
    """表示触摸效果的三角网格精灵类
    
    这个类创建一种特殊的视觉效果，模拟触摸屏幕时产生的三角形网格扩散效果。
    效果包括颜色渐变、大小变化、旋转和透明度变化。
    """
    
    # 类常量定义
    MIN_SIZE_FACTOR = 0.12  # 最小尺寸因子
    MAX_SIZE_FACTOR = 0.14  # 最大尺寸因子
    LIFE_DURATION = 0.6     # 生命周期（秒）
    INNER_RADIUS_RATIO = 15 / 16  # 内半径与外半径的比例
    SURFACE_HEIGHT_RATIO = 2 / 60  # 表面高度比例
    
    def __init__(self, speed, allsize, pattern, previous_pos):
        """
        初始化MeshTri对象
        
        Args:
            speed (float): 动画播放速度倍数
            allsize (float): 基准尺寸大小
            pattern (tuple): 包含多种特效图案的元组
            previous_pos (tuple): 触摸起始位置坐标 (x, y)
        """
        super().__init__()  # 调用父类Sprite的初始化方法
        
        # 基本属性设置
        self.type = "touch"  # 精灵类型标识
        self.initial_position = previous_pos  # 初始位置
        self.life = self.LIFE_DURATION  # 设置生命周期
        # 随机生成尺寸（在最小和最大因子之间）
        self.size = random.uniform(self.MIN_SIZE_FACTOR, self.MAX_SIZE_FACTOR) * allsize
        self.angle = random.randrange(0, 360)  # 随机初始旋转角度
        self.pattern = pattern[1]  # 选择第二个图案作为基础纹理
        self.image = self.pattern  # 设置初始图像
        self.rect = self.image.get_rect(center=self.initial_position)  # 设置碰撞矩形

        # 时间相关参数计算
        self.delta_time = 1 / (self.life * speed)  # 每帧时间增量
        self.speed = speed  # 保存速度参数
        self.time = 0  # 当前动画时间

        # 颜色变化控制数组：[[颜色RGB值], 时间点]
        # 控制特效在整个生命周期内的颜色过渡
        self.colors = [[(255, 255, 255), 0],      # 白色开始
                       [(255, 255, 255), 0.112],  # 白色保持一段时间
                       [(76, 167, 255), 0.5],     # 过渡到蓝色
                       [(76, 167, 255), 1],       # 蓝色结束
                       [(76, 167, 255), 1.1]]     # 超出范围保护
        self.color_index = 0  # 当前颜色索引

        # 数学函数定义：使用numpy多项式创建动画曲线
        # 这些函数控制特效的各种属性随时间的变化
        
        # 半径变化函数（两个阶段）
        self.radius_function_1 = np.poly1d(np.array([-12.757, 0.71344, 2.2467, 0.326]))
        self.radius_function_2 = np.poly1d(np.array([0.073546, -0.624, 1.027, 0.523]))
        
        # 宽度变化函数
        self.max_width_function_1 = np.poly1d(np.array([1.7513, -3.0175, 0.781, 0.9447]))
        self.min_width_function_1 = np.poly1d(np.array([2.9213, -5.076, 1.3881, 0.6956]))
        
        # 长度变化函数
        self.length_function_1 = np.poly1d(np.array([250, -75, 0, 1]))
        self.length_function_2 = np.poly1d(np.array([-3.90625, 7.03125, -2.34375, 0.21875]))

    def update(self, **kwargs):
        """更新精灵状态
        
        每帧调用此方法来更新特效的各项属性。
        包括位置、大小、颜色、旋转角度等。
        
        Args:
            **kwargs: 额外的关键字参数（在此实现中未使用）
        """
        # 初始化计算变量
        radius = max_width = min_width = 0
        
        # 计算当前半径大小
        if self.time <= 0.214:
            # 第一阶段：使用第一个半径函数
            radius = self.radius_function_1(self.time)
        elif self.time > 0.214 and self.time <= 1:
            # 第二阶段：使用第二个半径函数
            radius = self.radius_function_2(self.time)

        # 计算最大宽度
        if self.time <= 0.149:
            # 初始阶段：固定值
            max_width = 640 / self.speed * 1
        elif self.time > 0.149 and self.time <= 1:
            # 后续阶段：使用函数计算
            max_width = self.max_width_function_1(self.time)
            
        # 计算最小宽度
        if self.time <= 0.159:
            # 初始阶段：固定值
            min_width = 640 / self.speed * 0.8
        elif self.time > 0.159 and self.time <= 1:
            # 后续阶段：使用函数计算
            min_width = self.min_width_function_1(self.time)
            
        # 在最小和最大宽度间随机选择当前宽度
        width = random.uniform(min_width, max_width)

        # 计算长度因子
        if self.time <= 0.2:
            # 第一阶段
            length_factor = self.length_function_1(self.time)
        elif self.time > 0.2 and self.time <= 1:
            # 第二阶段
            length_factor = self.length_function_2(self.time)

        # 计算内外半径（基于当前半径和尺寸）
        inner_radius = max(0, int(radius * self.size * self.INNER_RADIUS_RATIO))
        outer_radius = max(0, int(radius * self.size * 1))
        
        # 创建绘图表面
        pattern_surface = pg.Surface((outer_radius * 2, outer_radius * 2), pg.SRCALPHA)
        average_radius = (inner_radius + outer_radius) / 2  # 平均半径用于定位
        current_color = change_color(self.colors, self.time)  # 获取当前颜色
        base_length = (outer_radius - inner_radius) * (1 - length_factor)  # 基础线长度
        
        # 绘制辐射状线条效果
        for angle in range(0, 360):
            # 计算每条线的长度（基于角度的渐变效果）
            line_length = base_length * abs(180 - angle) / 180
            if line_length > 0:  # 只绘制长度大于0的线
                # 创建单条线的表面
                line_surface = pg.Surface((line_length, math.ceil(outer_radius * 2 * self.SURFACE_HEIGHT_RATIO)), pg.SRCALPHA)
                line_surface.fill(current_color)  # 填充当前颜色
                
                # 计算线条在圆周上的位置
                dx = math.cos(math.radians(angle)) * average_radius
                dy = math.sin(math.radians(angle)) * average_radius
                
                # 旋转线条使其沿径向排列
                rotated_line = pg.transform.rotate(line_surface, -angle)
                
                # 将线条绘制到主表面上
                pattern_surface.blit(rotated_line, 
                                   (outer_radius + 1 + dx - rotated_line.get_size()[0] / 2, 
                                    outer_radius + 1 + dy - rotated_line.get_size()[1] / 2))

        # 应用整体旋转效果
        pattern_surface = pg.transform.rotate(pattern_surface, self.angle)
        
        # 更新精灵图像和位置
        self.image = pattern_surface
        self.rect = self.image.get_rect(center=self.initial_position)
        
        # 更新旋转角度和时间
        times, self.angle = divmod(self.angle + width, 360)  # 循环旋转角度
        self.time += self.delta_time  # 推进动画时间
        
        # 检查生命周期是否结束
        if self.time > 1:
            self.kill()  # 销毁精灵