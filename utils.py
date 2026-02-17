import ctypes
import numpy as np

def get_fps(default_fps = 60):
    """
    创建一个帧率计算器函数
    """
    import time
    t = None  # 初始化时间变量，用于存储上一帧的时间戳
    
    def fps():
        """
        内部函数，计算并返回当前帧率
        """
        nonlocal t  # 声明使用外层函数的变量t
        if t:
            # 非首次调用：计算帧率
            t0 = t  # 保存上一帧时间
            t = time.time()  # 更新当前时间
            return 1/(t - t0 + 0.000000001)  # 计算帧率，避免除零
        else:
            # 首次调用：初始化时间并返回默认帧率
            t = time.time()
            return default_fps
    return fps

class WindowsApiConstants:
    # Windows API常量
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    GWL_EXSTYLE = -20

def set_mouse_thru(hwnd):
    # 获取当前扩展样式
    current_style = ctypes.windll.user32.GetWindowLongW(hwnd, WindowsApiConstants.GWL_EXSTYLE)
    # 设置新的扩展样式（透明+分层）
    ctypes.windll.user32.SetWindowLongW(
        hwnd, 
        WindowsApiConstants.GWL_EXSTYLE, 
        current_style | WindowsApiConstants.WS_EX_LAYERED | WindowsApiConstants.WS_EX_TRANSPARENT
    )

def evaluate_piecewise_hermite(break_point, func1, func2):
    """分段hermite插值计算"""
    def evaluator(x):
        mask = np.asarray(x) < break_point
        return np.where(mask, func1(x), func2(x))
    return evaluator