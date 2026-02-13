import pygame as pg
import numpy as np
import random
import math

from img_utils import change_color, change_alpha, change_image_by_grayscale

class RingX(pg.sprite.Sprite):
    def __init__(self, speed, allsize, pattern, previous_pos, order):
        super().__init__()
        self.type = "touch"  # 精灵类型
        self.initial_position = previous_pos  # 初始位置
        self.scale_factor = 0.3 if order == 3 else 0.15 if order == 4 else 0  # 缩放因子
        self.lifetime = random.uniform(0.6, 0.7) if order == 3 else random.uniform(0.2, 0.4) if order == 4 else 0  # 生命周期
        self.initial_velocity = random.uniform(0.3, 0.4) * self.scale_factor if order == 3 else random.uniform(0.2, 0.3) * self.scale_factor if order == 4 else 0  # 初始速度
        self.base_size = random.uniform(0.1, 0.2) * allsize * self.scale_factor  # 基础大小
        self.pattern_image = pattern[random.randrange(1, 3)] if order == 4 else pattern[1]  # 图案图像
        self.image = self.pattern_image
        self.rect = self.image.get_rect(center=self.initial_position)
        self.ring_order = order  # 圆环顺序
        self.time_delta = 1 / (self.lifetime * speed)  # 时间增量
        self.current_time = 0  # 当前时间
        self.delta_distance = 5  # 距离增量

        # 颜色变化数组
        self.color_transitions = [[(255, 255, 255), 0],
                                  [(255, 255, 255), 0.182],
                                  [(95, 197, 255), 0.282],
                                  [(95, 197, 255), 0.462],
                                  [(90, 186, 241), 0.662],
                                  [(95, 197, 255), 0.826],
                                  [(95, 197, 255), 1],
                                  [(95, 197, 255), 1.1]]
        
        # 透明度变化数组
        self.alpha_transitions = [[255, 0],
                                  [255, 0.288],
                                  [0, 0.365],
                                  [255, 0.471],
                                  [0, 0.574],
                                  [255, 0.668],
                                  [0, 0.756],
                                  [255, 0.853],
                                  [255, 1],
                                  [255, 1.1]]
        
        angle = random.randrange(0, 360)  # 随机角度
        rad = math.radians(angle)  # 转换为弧度
        radius_factor = 0.3 if order == 3 else 0.15 if order == 4 else 0  # 半径因子
        self.displacement_x = math.cos(rad) * allsize * radius_factor * self.scale_factor  # X方向位移
        self.displacement_y = math.sin(rad) * allsize * radius_factor * self.scale_factor  # Y方向位移
        self.velocity_x = self.initial_velocity * math.cos(rad) * allsize * self.scale_factor  # X方向速度
        self.velocity_y = self.initial_velocity * math.sin(rad) * allsize * self.scale_factor  # Y方向速度

        # 用于计算缩放的多项式函数
        self.scale_function_1 = np.poly1d(np.array([-547, 126.3746, 0, 0]))
        self.scale_function_2 = np.poly1d(np.array([0.0878, -1.156, 0.0486, 1.02]))

    def update(self, **kwargs):
        scale_ratio = 0
        if self.current_time <= 0.154:
            scale_ratio = self.scale_function_1(self.current_time)
        elif self.current_time > 0.154 and self.current_time <= 1:
            scale_ratio = self.scale_function_2(self.current_time)
        
        scaled_size = (max(0, int(scale_ratio * self.base_size)), max(0, int(scale_ratio * self.base_size)))
        
        if scaled_size[0] != 0:
            current_color = change_color(self.color_transitions, self.current_time)
            current_alpha = change_alpha(self.alpha_transitions, self.current_time)
            scaled_pattern = pg.transform.scale(self.pattern_image, scaled_size)
            final_pattern = change_image_by_grayscale(scaled_pattern, current_color, current_alpha, 255, False)
        else:
            final_pattern = pg.Surface((1, 1), pg.SRCALPHA)
        
        self.image = final_pattern
        self.rect = self.image.get_rect(center=(self.initial_position[0] + self.displacement_x + self.velocity_x * self.current_time,
                                                self.initial_position[1] + self.displacement_y + self.velocity_y * self.current_time))

        self.current_time += self.time_delta

        if self.current_time > 1:
            self.kill()