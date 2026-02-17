import random

import numpy as np
from scipy.interpolate import interp1d, CubicHermiteSpline
from pynput import mouse

from img_utils import load_grayscale_image
from utils import evaluate_piecewise_hermite

class GlobalConstants:
    # (mouse.Button.left, mouse.Button.right, mouse.Button.middle, mouse.Button.x1, mouse.Button.x2)
    MOUSE_HIT_AREA = (mouse.Button.left, mouse.Button.right, mouse.Button.middle, mouse.Button.x1, mouse.Button.x2)

    SIZE = 256
    MAX_FPS = 60

    TOUCH_EFFECT_WIDGET_SIDE = 256

class MeshTriConstants:
    START_LIFETIME = 0.6
    START_SIZE = 0.12
    get_start_size = lambda self: random.uniform(0.12, 0.14)
    START_ROTATION = 0
    get_start_rotation = lambda self: random.uniform(0, 360)

    # === 颜色渐变配置 ===
    COLOR_KEY_POINTS = [
        {"channel": "r", "time_percentages": (0.0, 0.112, 0.5, 1.0), "values": (255, 255, 76, 76)},
        {"channel": "g", "time_percentages": (0.0, 0.112, 0.5, 1.0), "values": (255, 255, 167, 167)},
        {"channel": "b", "time_percentages": (0.0, 0.112, 0.5, 1.0), "values": (255, 255, 255, 255)},
        {"channel": "a", "time_percentages": (0.0, 1.0), "values": (255, 255)},
    ]
    COLOR_OVER_LIFETIME = tuple(
        interp1d(np.array(channel["time_percentages"]), np.array(channel["values"]), kind="linear")
        for channel in COLOR_KEY_POINTS
    )

    # === 尺寸变化配置 ===
    SIZE_KEY_POINTS = {
        "time_percentages": (0.0, 0.214, 1.0),
        "values": (0.652, 1.432, 2.0),          # 已预计算：0.326 * 2, 0.716 * 2
        "tangents": (2.4, 0.9, 0.0),
    }
    SIZE_OVER_LIFETIME = CubicHermiteSpline(
        SIZE_KEY_POINTS["time_percentages"],
        SIZE_KEY_POINTS["values"],
        SIZE_KEY_POINTS["tangents"]
    )

    # === 旋转变化配置 ===
    ROTATION_KEY_POINTS_MIN = {
        "time_percentages": (0.0, 0.159, 1.0),
        "values": (511.36, 511.36, -41.6),    # 已预计算：0.799 * 640, -0.065 * 640
        "tangents": (0.0, 0.0, 0.0),
    }
    ROTATION_OVER_LIFETIME_MIN = CubicHermiteSpline(
        ROTATION_KEY_POINTS_MIN["time_percentages"],
        ROTATION_KEY_POINTS_MIN["values"],
        ROTATION_KEY_POINTS_MIN["tangents"]
    )

    ROTATION_KEY_POINTS_MAX = {
        "time_percentages": (0.0, 0.149, 1.0),
        "values": (640.0, 640.0, 291.84),     # 已预计算：1 * 640, 0.456 * 640
        "tangents": (0.0, 0.0, 0.0),
    }
    ROTATION_OVER_LIFETIME_MAX = CubicHermiteSpline(
        ROTATION_KEY_POINTS_MAX["time_percentages"],
        ROTATION_KEY_POINTS_MAX["values"],
        ROTATION_KEY_POINTS_MAX["tangents"]
    )

    ROTATION_OVER_LIFETIME = lambda self, time: random.uniform(MeshTriConstants.ROTATION_OVER_LIFETIME_MIN(time), 
                                                         MeshTriConstants.ROTATION_OVER_LIFETIME_MAX(time))
    


    class Emission:
        COUNT = 2
        INTERVAL = 0.010

    class CustomData:
        CUSTOM1_X_KEY_POINTS = {
            "time_percentages": ((0.0, 0.2), (0.2, 1.0)),
            "values": ((1, 0), (0, 1)),
            "tangents": ((0, 0), (2.425, 0.277))
        }

        CUSTOM1_X = lambda time: 0
        @staticmethod
        def get_custom1_x():
            CUSTOM1_X_FUNCS = tuple(CubicHermiteSpline(
            MeshTriConstants.CustomData.CUSTOM1_X_KEY_POINTS["time_percentages"][i],
            MeshTriConstants.CustomData.CUSTOM1_X_KEY_POINTS["values"][i],
            MeshTriConstants.CustomData.CUSTOM1_X_KEY_POINTS["tangents"][i]) 
            for i in range(2))
            CUSTOM1_X = evaluate_piecewise_hermite(0.2, *CUSTOM1_X_FUNCS)
            return CUSTOM1_X

class RingConstants:
    # === 基础属性 ===
    START_LIFETIME = 0.2
    START_SIZE = 0.24
    START_ROTATION = 0
    get_start_rotation = lambda self: random.uniform(0, 360)

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
        "time_percentages": (0.0, 0.214, 1.0),
        "values": (0.652, 1.432, 2.0),          # 已预计算：0.326 * 2, 0.716 * 2
        "tangents": (2.4, 0.9, 0.0),
    }
    SIZE_OVER_LIFETIME = CubicHermiteSpline(
        SIZE_KEY_POINTS["time_percentages"],
        SIZE_KEY_POINTS["values"],
        SIZE_KEY_POINTS["tangents"]
    )

    # === 资源路径 ===
    GRAYSCALE_IMAGE_PATH = 'pictures/effects/FX_TEX_Circle_01.png'
    GRAYSCALE_IMAGE = load_grayscale_image(GRAYSCALE_IMAGE_PATH)


class RingXConstants:

    START_SIZE = 0.1
    get_start_size = lambda self: random.uniform(0.1, 0.2)

    START_LIFETIME = 0.2
    START_SPEED = 0.2

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

    # === 资源路径 ===
    GRAYSCALE_IMAGE_PATH = 'pictures/effects/FX_TEX_TRIangle_02.png'
    GRAYSCALE_IMAGE = load_grayscale_image(GRAYSCALE_IMAGE_PATH)


class Ring3Constants(RingXConstants):
    
    get_start_lifetime = lambda self: random.uniform(0.6, 0.7)
    get_start_speed = lambda self: random.uniform(0.3, 0.4)

    class Emission:
        COUNT = 4
        INTERVAL = 0.010

    class Shape:
        RADIUS = 1
        ARC = 360
        SCALE = (0.3, 0.3)

    
class Ring4Constants(RingXConstants):

    get_start_lifetime = lambda self: random.uniform(0.2, 0.4)
    get_start_speed = lambda self: random.uniform(0.2, 0.3)

    class Emission:
        RATE_OVER_DISTANCE = 5

    class Shape:
        RADIUS = 1
        ARC = 360
        SCALE = (0.15, 0.15)


class TrailConstants:
    pass

