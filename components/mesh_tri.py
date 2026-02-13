import pygame as pg
import numpy as np
import random
import math

from img_utils import change_color

class MeshTri(pg.sprite.Sprite):
    """表示触摸效果的三角网格精灵类"""
    
    # 常量定义
    MIN_SIZE_FACTOR = 0.12
    MAX_SIZE_FACTOR = 0.14
    LIFE_DURATION = 0.6
    INNER_RADIUS_RATIO = 15 / 16
    SURFACE_HEIGHT_RATIO = 2 / 60
    
    def __init__(self, speed, allsize, pattern, previous_pos):
        """
        初始化MeshTri对象
        
        Args:
            speed (float): 动画速度
            allsize (float): 基础大小
            pattern (tuple): 图案元组
            previous_pos (tuple): 初始位置
        """
        super().__init__()
        self.type = "touch"
        self.initial_position = previous_pos
        self.life = self.LIFE_DURATION
        self.size = random.uniform(self.MIN_SIZE_FACTOR, self.MAX_SIZE_FACTOR) * allsize
        self.angle = random.randrange(0, 360)
        self.pattern = pattern[1]
        self.image = self.pattern
        self.rect = self.image.get_rect(center=self.initial_position)

        self.delta_time = 1 / (self.life * speed)
        self.speed = speed
        self.time = 0

        # 颜色变化数组 [颜色, 时间点]
        self.colors = [[(255, 255, 255), 0],
                       [(255, 255, 255), 0.112],
                       [(76, 167, 255), 0.5],
                       [(76, 167, 255), 1],
                       [(76, 167, 255), 1.1]]
        self.color_index = 0

        # 定义各种数学函数用于动画计算
        self.radius_function_1 = np.poly1d(np.array([-12.757, 0.71344, 2.2467, 0.326]))
        self.radius_function_2 = np.poly1d(np.array([0.073546, -0.624, 1.027, 0.523]))
        self.max_width_function_1 = np.poly1d(np.array([1.7513, -3.0175, 0.781, 0.9447]))
        self.min_width_function_1 = np.poly1d(np.array([2.9213, -5.076, 1.3881, 0.6956]))
        self.length_function_1 = np.poly1d(np.array([250, -75, 0, 1]))
        self.length_function_2 = np.poly1d(np.array([-3.90625, 7.03125, -2.34375, 0.21875]))

    def update(self, **kwargs):
        """更新精灵状态"""
        radius = max_width = min_width = 0
        
        # 计算半径
        if self.time <= 0.214:
            radius = self.radius_function_1(self.time)
        elif self.time > 0.214 and self.time <= 1:
            radius = self.radius_function_2(self.time)

        # 计算最大宽度
        if self.time <= 0.149:
            max_width = 640 / self.speed * 1
        elif self.time > 0.149 and self.time <= 1:
            max_width = self.max_width_function_1(self.time)
            
        # 计算最小宽度
        if self.time <= 0.159:
            min_width = 640 / self.speed * 0.8
        elif self.time > 0.159 and self.time <= 1:
            min_width = self.min_width_function_1(self.time)
            
        width = random.uniform(min_width, max_width)

        # 计算长度因子
        if self.time <= 0.2:
            length_factor = self.length_function_1(self.time)
        elif self.time > 0.2 and self.time <= 1:
            length_factor = self.length_function_2(self.time)

        # 计算内外半径
        inner_radius = max(0, int(radius * self.size * self.INNER_RADIUS_RATIO))
        outer_radius = max(0, int(radius * self.size * 1))
        
        # 创建图案表面
        pattern_surface = pg.Surface((outer_radius * 2, outer_radius * 2), pg.SRCALPHA)
        average_radius = (inner_radius + outer_radius) / 2
        current_color = change_color(self.colors, self.time)
        base_length = (outer_radius - inner_radius) * (1 - length_factor)
        
        # 绘制辐射线
        for angle in range(0, 360):
            line_length = base_length * abs(180 - angle) / 180
            if line_length > 0:
                line_surface = pg.Surface((line_length, math.ceil(outer_radius * 2 * self.SURFACE_HEIGHT_RATIO)), pg.SRCALPHA)
                line_surface.fill(current_color)
                dx = math.cos(math.radians(angle)) * average_radius
                dy = math.sin(math.radians(angle)) * average_radius
                rotated_line = pg.transform.rotate(line_surface, -angle)
                pattern_surface.blit(rotated_line, 
                                   (outer_radius + 1 + dx - rotated_line.get_size()[0] / 2, 
                                    outer_radius + 1 + dy - rotated_line.get_size()[1] / 2))

        # 应用旋转和更新精灵
        pattern_surface = pg.transform.rotate(pattern_surface, self.angle)
        self.image = pattern_surface
        self.rect = self.image.get_rect(center=self.initial_position)
        times, self.angle = divmod(self.angle + width, 360)
        self.time += self.delta_time
        if self.time > 1:
            self.kill()