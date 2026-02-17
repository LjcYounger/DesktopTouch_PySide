import random

import numpy as np
from scipy.interpolate import interp1d, CubicHermiteSpline
from pynput import mouse

from img_utils import load_grayscale_image

class GlobalConstants:
    # (mouse.Button.left, mouse.Button.right, mouse.Button.middle, mouse.Button.x1, mouse.Button.x2)
    MOUSE_HIT_AREA = (mouse.Button.left, mouse.Button.right, mouse.Button.middle, mouse.Button.x1, mouse.Button.x2)

    SIZE = 512

class MeshTriConstants:
    START_LIFETIME = 0.6

class RingConstants:
    # === 基础属性 ===
    START_LIFETIME = 0.2
    START_SIZE = 0.12

    # === 颜色渐变配置 ===
    COLOR_KEY_POINTS = [
        {"channel": "r", "time_percentages": (0.0, 0.121, 1.0), "values": (255, 61, 61)},
        {"channel": "g", "time_percentages": (0.0, 0.121, 1.0), "values": (255, 100, 100)},
        {"channel": "b", "time_percentages": (0.0, 0.121, 1.0), "values": (255, 255, 255)},
        {"channel": "a", "time_percentages": (0.0, 0.109, 1.0), "values": (255, 255, 0)},
    ]
    COLOR_OVER_LIFETIME = tuple(
        interp1d(np.array(channel["time_percentages"]), np.array(channel["values"]), kind="linear")
        for channel in COLOR_KEY_POINTS
    )

    # === 尺寸变化配置 ===
    SIZE_KEY_POINTS = {
        "time_percentages": (0.0, 0.428, 1.0),  # 已预计算：0.214 * 2
        "values": (0.326, 1.432, 1.0),          # 已预计算：0.716 * 2
        "tangents": (2.4, 1.8, 0.0),            # 已预计算：0.9 * 2
    }
    SIZE_OVER_LIFETIME = CubicHermiteSpline(
        SIZE_KEY_POINTS["time_percentages"],
        SIZE_KEY_POINTS["values"],
        SIZE_KEY_POINTS["tangents"]
    )

    # === 资源路径 ===
    GRAYSCALE_IMAGE_PATH = 'pictures/effects/FX_TEX_Circle_01.png'
    GRAYSCALE_IMAGE = load_grayscale_image(GRAYSCALE_IMAGE_PATH)

    # === 工具方法 ===
    @staticmethod
    def get_start_rotation():
        return random.uniform(0, 360)

class RingXConstants:

    # === 颜色渐变配置 ===
    COLOR_KEY_POINTS = [
        {"channel": "r", "time_percentages": (0.0, 0.182, 0.282, 0.462, 0.662, 0.826, 1.0), "values": (255, 255, 95, 95, 90, 95, 95)},
        {"channel": "g", "time_percentages": (0.0, 0.182, 0.282, 0.462, 0.662, 0.826, 1.0), "values": (255, 255, 197, 197, 186, 197, 197)},
        {"channel": "b", "time_percentages": (0.0, 0.182, 0.282, 0.462, 0.662, 0.826, 1.0), "values": (255, 255, 255, 255, 241, 255, 255)},
        {"channel": "a", "time_percentages": (0.0, 0.288, 0.365, 0.471, 0.574, 0.668, 0.756, 0.853, 1.0), "values": (255, 255, 0, 255, 0, 255, 0, 255, 255)},
    ]
    COLOR_OVER_LIFETIME = tuple(
        interp1d(np.array(channel["time_percentages"]), np.array(channel["values"]), kind="linear")
        for channel in COLOR_KEY_POINTS
    )

    # === 尺寸变化配置 ===
    SIZE_KEY_POINTS = {
        "time_percentages": (0.0, 0.154451, 1.0),
        "values": (0.0, 1.0, 0.0),
        "tangents": (0.0, 0.0, -2.162),
    }
    SIZE_OVER_LIFETIME = CubicHermiteSpline(
        SIZE_KEY_POINTS["time_percentages"],
        SIZE_KEY_POINTS["values"],
        SIZE_KEY_POINTS["tangents"]
    )

    @staticmethod
    def get_start_size():
        return random.uniform(0.1, 0.2)

class Ring3Constants(RingXConstants):

    class Emission:
        COUNT = 4
        INTERVAL = 0.010
    @staticmethod
    def get_start_lifetime():
        return random.uniform(0.6, 0.7)
    
    @staticmethod
    def get_start_speed():
        return random.uniform(0.3, 0.4)
    
class Ring4Constants(RingXConstants):

    class Emission:
        RATE_OVER_DISTANCE = 5
    @staticmethod
    def get_start_lifetime():
        return random.uniform(0.2, 0.4)
    
    @staticmethod
    def get_start_speed():
        return random.uniform(0.2, 0.3)

class TrailConstants:
    pass

class WindowsApiConstants:
    # Windows API常量
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    GWL_EXSTYLE = -20