# cython: language_level=3
import numpy as np
cimport numpy as np
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from functools import lru_cache
from typing import Tuple

# 使用C类型声明
ctypedef np.uint8_t uint8
ctypedef np.float32_t float32

# 缓存颜色转换结果
@lru_cache(maxsize=128)
def _get_color_multiplier(color: Tuple[int, int, int]) -> np.ndarray:
    """缓存颜色乘数计算"""
    return np.array(color, dtype=np.float32) / 255.0

cpdef load_grayscale_image(str image_path):
    return QImage(image_path)

cpdef split_image_vertically(image):
    """
    将QImage从中间竖直对半切割
    """
    cdef int width = image.width()
    cdef int height = image.height()
    cdef int mid_x = width // 2
    
    return (image.copy(0, 0, mid_x, height), 
            image.copy(mid_x, 0, width - mid_x, height))

cpdef slice_image_vertically(image):
    """
    将QImage按1像素宽度竖直切片
    """
    cdef int width = image.width()
    cdef int height = image.height()
    
    return [image.copy(x, 0, 1, height) for x in range(width)]

cpdef change_image_by_grayscale(
    image,
    tuple color,
    int alpha,
    bint grayscale_image_transparent=False,
    int impact_on_transparency=255,
    bint invert_grayscale=False
):
    """
    修复后的灰度图像着色处理函数
    """
    # 确保图像是ARGB32格式
    if image.format() != QImage.Format_ARGB32:
        image = image.convertToFormat(QImage.Format_ARGB32)
    
    cdef int width = image.width()
    cdef int height = image.height()
    
    # 创建图像数据的深拷贝，确保数据独立
    cdef np.ndarray[np.uint8_t, ndim=3] img_array = np.frombuffer(
        image.constBits(), 
        dtype=np.uint8
    ).reshape((height, width, 4)).copy()  # 添加copy()确保数据独立
    
    # 预处理颜色乘数
    cdef np.ndarray[np.float32_t] color_mult = _get_color_multiplier(color)
    cdef np.ndarray[np.float32_t] color_mult_255 = color_mult * 255
    
    # 获取灰度值(向量化操作)
    cdef np.ndarray[np.uint8_t, ndim=2] gray_values = img_array[:, :, 1].copy()
    
    # 灰度反转(向量化)
    if invert_grayscale:
        gray_values = 255 - gray_values
    
    # 归一化灰度(向量化)
    cdef np.ndarray[np.float32_t, ndim=2] gray_normalized = gray_values.astype(np.float32) / 255.0
    
    # 创建结果数组
    cdef np.ndarray[np.uint8_t, ndim=3] result = np.empty((height, width, 4), dtype=np.uint8)
    
    # 计算RGB通道(向量化)
    result[:, :, 2] = (color_mult_255[0] * gray_normalized).astype(np.uint8)  # R
    result[:, :, 1] = (color_mult_255[1] * gray_normalized).astype(np.uint8)  # G
    result[:, :, 0] = (color_mult_255[2] * gray_normalized).astype(np.uint8)  # B
    
    # 处理Alpha通道(向量化)
    cdef float32 alpha_factor = alpha / impact_on_transparency
    if grayscale_image_transparent:
        result[:, :, 3] = img_array[:, :, 3]  # 保留原Alpha
    else:
        result[:, :, 3] = np.clip((gray_values * alpha_factor).astype(np.uint8), 0, 255)
    
    # 创建QImage时确保数据独立
    cdef bytes result_bytes = result.tobytes()
    result_image = QImage(
        result_bytes, 
        width, 
        height, 
        width * 4, 
        QImage.Format_ARGB32
    )
    
    return QPixmap.fromImage(result_image.copy())