from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
from PySide6.QtGui import QImage, QPixmap, qRed, qGreen, qBlue, qAlpha
from PySide6.QtCore import Qt

def load_grayscale_image(image_path: str) -> QImage:
    return QImage(image_path)

import numpy as np
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

def change_image_by_grayscale(image: QImage, 
                              color: tuple, 
                              alpha: int, 
                              impact_on_transparency: int=255, 
                              invert_grayscale: bool=False):
    """
    将灰度图像转换为指定颜色和透明度的彩色图像（使用numpy优化）
    
    Args:
        image (QImage): 输入的灰度图像
        color (tuple): 目标RGB颜色值 (r, g, b)
        alpha (int): 透明度值 (0-255)
        impact_on_transparency (int): 透明度影响因子 (0-255)
        invert_grayscale (bool): 是否反转灰度值
        
    Returns:
        QPixmap: 转换后的彩色图像
    """
    # 确保图像是Format_ARGB32格式
    if image.format() != QImage.Format.Format_ARGB32:
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
    
    # 将QImage转换为numpy数组
    width = image.width()
    height = image.height()
    
    # 使用memoryview获取图像数据
    ptr = image.bits()
    img_array = np.frombuffer(ptr, dtype=np.uint8)
    img_array = img_array.reshape((height, width, 4))  # ARGB格式
    
    # 提取灰度值（假设RGB相同，取其中一个通道）
    gray_values = img_array[:, :, 1].astype(np.float32)  # Green channel
    
    # 处理灰度反转
    if invert_grayscale:
        gray_values = 255 - gray_values
    
    # 归一化灰度值
    gray_normalized = gray_values / 255.0
    
    # 解包目标颜色
    target_r, target_g, target_b = color
    
    # 计算新的RGB值
    new_r = (target_r * gray_normalized).astype(np.uint8)
    new_g = (target_g * gray_normalized).astype(np.uint8)
    new_b = (target_b * gray_normalized).astype(np.uint8)
    
    # 计算新的Alpha值
    new_a = (alpha * gray_values / impact_on_transparency).astype(np.uint8)
    new_a = np.clip(new_a, 0, 255)  # 限制在0-255范围内
    
    # 组合成新的ARGB图像数组（注意Qt使用BGRA顺序）
    result_array = np.stack([new_b, new_g, new_r, new_a], axis=2)
    
    # 创建新的QImage
    result_image = QImage(result_array.data, width, height, QImage.Format.Format_ARGB32)
    # 确保数据独立，避免内存释放问题
    result_image = result_image.copy()
    
    return QPixmap.fromImage(result_image)

def thicken_lines(surface, thickness):
    """
    加粗图像中的线条
    
    Args:
        surface (pygame.Surface): 输入图像表面
        thickness (int): 加粗程度
        
    Returns:
        numpy.ndarray: 加粗后的RGBA数组
        
    实现方法:
        通过多次膨胀操作扩展线条的Alpha通道，
        然后将膨胀后的Alpha应用到原图像的RGB通道上。
    """
    # 提取RGB和Alpha通道
    rgb_array = pg.surfarray.array3d(surface)
    alpha_array = pg.surfarray.array_alpha(surface)
    
    # 创建膨胀后的alpha通道
    thickened_alpha = alpha_array.copy()
    for _ in range(thickness):
        # 在四个方向上进行膨胀操作
        thickened_alpha = np.maximum(
            np.maximum(thickened_alpha,
            np.roll(thickened_alpha, 1, axis=0),    # 上方
            np.roll(thickened_alpha, -1, axis=0)),   # 下方
            np.roll(thickened_alpha, 1, axis=1),     # 左侧
            np.roll(thickened_alpha, -1, axis=1)     # 右侧
        )
    
    # 应用加粗后的alpha到RGB
    result = np.dstack((rgb_array, thickened_alpha))
    return result

def apply_glow_effect(surface, thickness, blur_sigma):
    """
    结合膨胀和高斯模糊实现发光效果
    
    Args:
        surface (pygame.Surface): 输入图像表面
        thickness (int): 发光边缘厚度
        blur_sigma (float): 高斯模糊标准差
        
    Returns:
        pygame.Surface: 带发光效果的图像表面
        
    实现步骤:
        1. 膨胀操作扩展发光区域
        2. 分别对RGB和Alpha通道应用高斯模糊
        3. 创建发光层
        4. 将发光层与原始图像混合
    """
    # 1. 膨胀操作扩展发光区域
    dilated_array = thicken_lines(surface, thickness)
    
    # 2. 提取RGB和alpha通道
    rgb_array = dilated_array[:, :, :3]
    alpha_array = dilated_array[:, :, -1]
    
    # 3. 对RGB通道应用高斯模糊
    blurred_rgb = np.zeros_like(rgb_array)
    for c in range(3):  # 分别处理R、G、B三个通道
        blurred_rgb[:,:,c] = gaussian_filter(rgb_array[:,:,c], sigma=blur_sigma)
    
    # 4. 对alpha通道也进行模糊处理
    blurred_alpha = gaussian_filter(alpha_array.astype(float), sigma=blur_sigma)
    blurred_alpha = np.clip(blurred_alpha, 0, 255).astype(np.uint8)
    width, height = surface.get_size()
    
    # 5. 创建发光层
    glow_array = np.dstack((blurred_rgb, blurred_alpha))
    result_bytes = glow_array.tobytes()
    glow_surface = pg.image.frombuffer(result_bytes, (height, width), "RGBA")
    # 调整图像方向（旋转和翻转）
    glow_surface = pg.transform.rotate(glow_surface, -90)
    glow_surface = pg.transform.flip(glow_surface, True, False)
    
    # 6. 混合原始图像和发光层
    result = pg.Surface(surface.get_size(), pg.SRCALPHA)
    result.blit(glow_surface, (0, 0))  # 先绘制发光层
    result.blit(surface, (0, 0))       # 再绘制原始图像
    
    return result