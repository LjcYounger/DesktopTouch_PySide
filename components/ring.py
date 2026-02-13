import pygame as pg
import numpy as np

from img_utils import change_color, change_alpha, change_image_by_grayscale


class Ring(pg.sprite.Sprite):
    """触摸圆环特效类
    
    创建一个随时间变化的圆形扩散特效，包含颜色渐变、透明度变化和尺寸缩放效果。
    """
    
    def __init__(self, animation_speed, max_size, effect_patterns, initial_position):
        """初始化圆环特效
        
        Args:
            animation_speed (float): 动画播放速度
            max_size (int): 最大尺寸基准值
            effect_patterns (list): 特效图案列表
            initial_position (tuple): 初始位置坐标 (x, y)
        """
        super().__init__()
        
        # 基本属性
        self.type = "touch"  # 精灵类型标识
        self.initial_position = initial_position  # 初始中心位置
        self.lifetime = 0.2  # 特效生命周期（秒）
        self.base_size = 0.12 * max_size  # 基础尺寸
        self.pattern_image = effect_patterns[0]  # 使用第一个图案作为基础纹理
        self.image = self.pattern_image
        self.rect = self.image.get_rect(center=self.initial_position)
        
        # 时间控制参数
        self.time_delta = 1 / (self.lifetime * animation_speed)  # 每帧时间增量
        self.current_time = 0  # 当前动画时间
        
        # 颜色过渡定义：[(RGB颜色值), 时间点]
        self.color_transitions = [
            [(255, 255, 255), 0],      # 白色开始
            [(255, 255, 255), 0.112],  # 白色保持
            [(76, 167, 255), 0.5],     # 蓝色过渡
            [(76, 167, 255), 1],       # 蓝色结束
            [(76, 167, 255), 1.1]      # 超出范围保护
        ]
        
        # 透明度过渡定义：[透明度值, 时间点]
        self.alpha_transitions = [
            [255, 0],      # 不透明开始
            [255, 0.109],  # 不透明保持
            [8, 0.971],    # 半透明过渡
            [0, 1],        # 完全透明
            [0, 1.1]       # 超出范围保护
        ]
        
        # 阶段切换阈值
        self.transition_threshold = 0.214
        
        # 两个阶段的多项式函数用于计算半径缩放因子
        # 第一阶段：快速扩张
        self.expansion_polynomial = np.poly1d([-12.757, 0.71344, 2.2467, 0.326])
        # 第二阶段：缓慢收缩  
        self.contraction_polynomial = np.poly1d([0.073546, -0.624, 1.027, 0.523])
        
        # 当前状态索引（未使用但保留以保持兼容性）
        self.state_index = 0

    def update(self, **kwargs):
        """更新圆环特效状态
        
        每帧调用此方法来更新特效的位置、大小、颜色和透明度。
        当特效生命周期结束时自动销毁精灵。
        """
        # 根据当前时间选择合适的多项式计算半径缩放因子
        if self.current_time <= self.transition_threshold:
            # 第一阶段：快速扩张期
            radius_multiplier = 2 * self.expansion_polynomial(self.current_time)
        elif self.current_time > self.transition_threshold and self.current_time <= 1:
            # 第二阶段：缓慢收缩期
            radius_multiplier = 2 * self.contraction_polynomial(self.current_time)
        else:
            # 超出正常范围的情况
            radius_multiplier = 0

        # 计算缩放后的尺寸，确保不为负数
        scaled_width = max(0, int(radius_multiplier * self.base_size))
        scaled_height = max(0, int(radius_multiplier * self.base_size))
        scaled_size = (scaled_width, scaled_height)

        # 根据缩放尺寸生成对应的图像
        if scaled_size[0] != 0 and scaled_size[1] != 0:
            # 获取当前时间对应的颜色和透明度
            current_color = change_color(self.color_transitions, self.current_time)
            current_alpha = change_alpha(self.alpha_transitions, self.current_time)
            
            # 缩放基础图案到目标尺寸
            scaled_pattern = pg.transform.scale(self.pattern_image, scaled_size)
            
            # 应用颜色和透明度变换
            final_pattern = change_image_by_grayscale(
                scaled_pattern, 
                current_color, 
                current_alpha, 
                255,  # 最大强度
                False  # 不反转灰度
            )
        else:
            # 尺寸为零时创建一个像素的透明表面
            final_pattern = pg.Surface((1, 1), pg.SRCALPHA)
            
        # 更新精灵图像和矩形位置
        self.image = final_pattern
        self.rect = self.image.get_rect(center=self.initial_position)

        # 更新时间并检查是否应该销毁
        self.current_time += self.time_delta
        if self.current_time > 1:
            self.kill()  # 生命周期结束，移除精灵