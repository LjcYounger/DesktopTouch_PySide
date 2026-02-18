import math
import random
from typing import List

from PySide6.QtGui import QPixmap, QPainter, QTransform

from constants import GlobalConstants
from generate_frame import generate_animated_frame

class RingX:
    """触摸圆环特效类"""
    def __init__(self, constants) -> None:
        self.constants = constants
        self.constants.START_LIFETIME = self.constants.get_start_lifetime()
        self.constants.START_SPEED = self.constants.get_start_speed()
        self.constants.START_SIZE = self.constants.get_start_size()

        self.flip_transform = QTransform()
        self.flip_transform.scale(1, -1)

        self.assumed_elapsed_time = self.constants.Shape.RADIUS / self.constants.START_SPEED
        self.velocities = tuple(self.get_random_velocity() for _ in range(self.constants.Emission.COUNT))

    def get_frame(self, time) -> List[QPixmap] | None:
        """
        根据时间生成当前帧的QPixmap
        """
        return generate_animated_frame(time, self.constants, grayscale_image_transparent=True)

    def get_random_velocity(self):
        """
        生成随机方向的速度分量
        
        Returns:
            tuple[float, float]: (velocity_x, velocity_y) 速度分量
        """
        # 生成随机起始角度（0-360度）
        angle = random.uniform(0, self.constants.Shape.ARC)
        # 将角度转换为弧度
        angle_rad = math.radians(angle)
        
        # 计算x和y方向的速度分量
        velocity_x = self.constants.START_SPEED * math.cos(angle_rad) * self.constants.Shape.SCALE[0]
        velocity_y = self.constants.START_SPEED * math.sin(angle_rad) * self.constants.Shape.SCALE[1]
        
        return (velocity_x, velocity_y)
        
    def calculate_current_position(self, start_position: tuple, velocity: tuple,time: float):
        """
        根据起始位置、速度和时间计算当前位置
        """
        return tuple((start_position[i] + velocity[i] * (self.assumed_elapsed_time + time) * GlobalConstants.SIZE)
                     for i in range(2))