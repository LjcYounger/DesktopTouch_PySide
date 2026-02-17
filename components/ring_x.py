import pygame as pg
import numpy as np
import random
import math

from img_utils import change_color, change_alpha, change_image_by_grayscale

class RingX(pg.sprite.Sprite):
    """
    扩展环形特效类
    
    创建一种特殊的环形扩散特效，相比基础Ring类具有更多变化：
    - 支持多层级效果（order参数控制）
    - 随机的位置偏移和运动方向
    - 更复杂的缩放动画曲线
    """
    
    def __init__(self, speed, allsize, pattern, previous_pos, order):
        """
        初始化RingX对象
        
        Args:
            speed (float): 动画播放速度倍数
            allsize (float): 基准尺寸大小
            pattern (list): 特效图案列表
            previous_pos (tuple): 起始位置坐标 (x, y)
            order (int): 环形等级（3或4，影响效果参数）
        """
        super().__init__()
        
        # 基本属性
        self.type = "touch"  # 精灵类型标识
        self.initial_position = previous_pos  # 初始中心位置
        
        # 根据等级设置不同的参数
        self.scale_factor = 0.3 if order == 3 else 0.15 if order == 4 else 0  # 缩放因子
        self.lifetime = random.uniform(0.6, 0.7) if order == 3 else random.uniform(0.2, 0.4) if order == 4 else 0  # 生命周期
        self.initial_velocity = random.uniform(0.3, 0.4) * self.scale_factor if order == 3 else random.uniform(0.2, 0.3) * self.scale_factor if order == 4 else 0  # 初始速度
        self.base_size = random.uniform(0.1, 0.2) * allsize * self.scale_factor  # 基础尺寸
        self.pattern_image = pattern[random.randrange(1, 3)] if order == 4 else pattern[1]  # 图案选择
        self.image = self.pattern_image
        self.rect = self.image.get_rect(center=self.initial_position)
        self.ring_order = order  # 环形等级
        self.time_delta = 1 / (self.lifetime * speed)  # 时间增量
        self.current_time = 0  # 当前动画时间
        self.delta_distance = 5  # 距离增量（未使用）

        # 颜色过渡控制数组
        self.color_transitions = [[(255, 255, 255), 0],      # 白色开始
                                  [(255, 255, 255), 0.182],  # 白色保持
                                  [(95, 197, 255), 0.282],   # 浅蓝过渡
                                  [(95, 197, 255), 0.462],   # 浅蓝保持
                                  [(90, 186, 241), 0.662],   # 中蓝过渡
                                  [(95, 197, 255), 0.826],   # 浅蓝回归
                                  [(95, 197, 255), 1],       # 浅蓝结束
                                  [(95, 197, 255), 1.1]]     # 超出保护
        
        # 透明度过渡控制数组
        self.alpha_transitions = [[255, 0],      # 不透明开始
                                  [255, 0.288],  # 不透明保持
                                  [0, 0.365],    # 完全透明
                                  [255, 0.471],  # 不透明
                                  [0, 0.574],    # 透明
                                  [255, 0.668],  # 不透明
                                  [0, 0.756],    # 透明
                                  [255, 0.853],  # 不透明
                                  [255, 1],      # 不透明结束
                                  [255, 1.1]]    # 超出保护
        
        # 随机运动参数计算
        angle = random.randrange(0, 360)  # 随机角度
        rad = math.radians(angle)  # 转换为弧度
        radius_factor = 0.3 if order == 3 else 0.15 if order == 4 else 0  # 半径因子
        # 计算初始位移和速度向量
        self.displacement_x = math.cos(rad) * allsize * radius_factor * self.scale_factor
        self.displacement_y = math.sin(rad) * allsize * radius_factor * self.scale_factor
        self.velocity_x = self.initial_velocity * math.cos(rad) * allsize * self.scale_factor
        self.velocity_y = self.initial_velocity * math.sin(rad) * allsize * self.scale_factor

        # 缩放动画函数（两个阶段的多项式）
        self.scale_function_1 = np.poly1d(np.array([-547, 126.3746, 0, 0]))  # 第一阶段
        self.scale_function_2 = np.poly1d(np.array([0.0878, -1.156, 0.0486, 1.02]))  # 第二阶段

    def update(self, **kwargs):
        """
        更新RingX精灵状态
        
        实现复杂的位置移动、缩放、颜色和透明度变化效果
        """
        # 根据时间计算缩放比例
        scale_ratio = 0
        if self.current_time <= 0.154:
            # 第一阶段：快速缩放
            scale_ratio = self.scale_function_1(self.current_time)
        elif self.current_time > 0.154 and self.current_time <= 1:
            # 第二阶段：精细调整
            scale_ratio = self.scale_function_2(self.current_time)
        
        # 计算缩放后的尺寸
        scaled_size = (max(0, int(scale_ratio * self.base_size)), max(0, int(scale_ratio * self.base_size)))
        
        # 生成最终图像
        if scaled_size[0] != 0:
            # 获取当前颜色和透明度
            current_color = change_color(self.color_transitions, self.current_time)
            current_alpha = change_alpha(self.alpha_transitions, self.current_time)
            # 缩放图案
            scaled_pattern = pg.transform.scale(self.pattern_image, scaled_size)
            # 应用颜色和透明度变换
            final_pattern = change_image_by_grayscale(scaled_pattern, current_color, current_alpha, 255, False)
        else:
            # 尺寸为零时创建占位表面
            final_pattern = pg.Surface((1, 1), pg.SRCALPHA)
        
        # 更新图像和位置
        self.image = final_pattern
        # 计算当前位置（初始位置 + 位移 + 速度*时间）
        self.rect = self.image.get_rect(center=(
            self.initial_position[0] + self.displacement_x + self.velocity_x * self.current_time,
            self.initial_position[1] + self.displacement_y + self.velocity_y * self.current_time
        ))

        # 更新时间并检查生命周期
        self.current_time += self.time_delta
        if self.current_time > 1:
            self.kill()  # 生命周期结束，销毁精灵