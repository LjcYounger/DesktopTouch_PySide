import pygame as pg
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter


def change_color(colors, time):
     for n in range(0, len(colors)):
          if time >= colors[n][1] and time < colors[n + 1][1]:
               break
     part1 = colors[n]
     part2 = colors[n + 1]
     color = tuple(x1 + (x2 - x1) * (time - part1[1]) / (part2[1] - part1[1]) for x1, x2 in zip(part1[0], part2[0]))
     color = tuple(0 if x < 0 else 255 if x > 255 else x for x in color)
     return color

def change_alpha(alphas, time):
     for n in range(0, len(alphas)):
          if time >= alphas[n][1] and time < alphas[n + 1][1]:
               break
     a1 = alphas[n]
     a2 = alphas[n + 1]
     alpha = a1[0] + (a2[0] - a1[0]) * (time - a1[1]) / (a2[1] - a1[1])
     alpha = 0 if alpha < 0 else 255 if alpha > 255 else alpha
     return alpha

def change_image_by_grayscale(image, color, alpha, extent, trans):
     img_array0 = np.array(Image.frombytes("RGBA", image.get_size(), pg.image.tostring(image, "RGBA")))
     grayscale = img_array0[:, :, 0]
     img_array = np.zeros_like(img_array0)
     for i in range(3):
          img_array[:, :, i] = color[i] * (grayscale / 255)
     if trans:
          grayscale = 255 - grayscale
     new_alpha = grayscale * alpha // extent
     img_array[:, :, 3] = new_alpha
     result_bytes = img_array.tobytes()
     result_image = pg.image.frombuffer(result_bytes, (image.get_size()[1], image.get_size()[0]), "RGBA")
     return result_image

def thicken_lines(surface, thickness):
    """
    加粗图像中的线条
    """
    rgb_array = pg.surfarray.array3d(surface)
    alpha_array = pg.surfarray.array_alpha(surface)
    
    # 创建膨胀后的alpha通道
    thickened_alpha = alpha_array.copy()
    for _ in range(thickness):
        thickened_alpha = np.maximum(
            np.maximum(thickened_alpha,
            np.roll(thickened_alpha, 1, axis=0),  # 上
            np.roll(thickened_alpha, -1, axis=0)),  # 下
            np.roll(thickened_alpha, 1, axis=1),   # 左
            np.roll(thickened_alpha, -1, axis=1)   # 右
        )
    
    # 应用加粗后的alpha到RGB
    result = np.dstack((rgb_array, thickened_alpha))
    return result

def apply_glow_effect(surface, thickness, blur_sigma):
    """
    结合膨胀和高斯模糊实现发光效果
    """
    # 1. 膨胀操作扩展发光区域
    dilated_array = thicken_lines(surface, thickness)
    
    # 2. 提取RGB和alpha
    rgb_array = dilated_array[:, :, :3]
    alpha_array = dilated_array[:, :, -1]
    
    # 3. 对RGB通道应用高斯模糊
    blurred_rgb = np.zeros_like(rgb_array)
    for c in range(3):
        blurred_rgb[:,:,c] = gaussian_filter(rgb_array[:,:,c], sigma=blur_sigma)
    
    # 4. 对alpha通道也模糊
    blurred_alpha = gaussian_filter(alpha_array.astype(float), sigma=blur_sigma)
    blurred_alpha = np.clip(blurred_alpha, 0, 255).astype(np.uint8)
    width, height = surface.get_size()
    # 5. 创建发光层
    glow_array = np.dstack((blurred_rgb, blurred_alpha))
    result_bytes = glow_array.tobytes()
    glow_surface = pg.image.frombuffer(result_bytes, (height, width), "RGBA")
    glow_surface = pg.transform.rotate(glow_surface, -90)
    glow_surface = pg.transform.flip(glow_surface, True, False)
    # 6. 混合原始图像和发光层
    result = pg.Surface(surface.get_size(), pg.SRCALPHA)
    result.blit(glow_surface, (0, 0))
    result.blit(surface, (0, 0))
    
    return result