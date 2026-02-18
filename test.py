import numpy as np
from PIL import Image, ImageDraw
import os
import imageio
import math
from components.mesh_tri import MeshTriConstants

# ==============================
# 参数设置
# ==============================
WIDTH, HEIGHT = 512, 512       # 固定画布大小
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2  # 圆心位置
RADIUS = 200                   # 最大半径
FPS = 30                       # 视频帧率
DURATION = 1                  # 动画总时长（秒）
FRAMES = int(FPS * DURATION)   # 总帧数

# ==============================
# 自定义时间函数（假设你已准备好）
# ==============================
get_t = MeshTriConstants.CustomData.get_custom1_x()

# ==============================
# 绘制动态月牙形图像
# ==============================
def draw_dynamic_crescent(progress, rotation_angle=0):
    """
    根据进度值 progress ∈ [0, 1] 和旋转角度绘制动态月牙
    """
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))  # 透明背景
    draw = ImageDraw.Draw(img)

    # 动态参数
    inner_radius = int(RADIUS * 0.6 * progress)  # 内圈半径
    outer_radius = int(RADIUS * progress)        # 外圈半径
    line_count = int(100 * progress)             # 线条数量
    max_line_length = outer_radius - inner_radius  # 最大线长

    # 颜色渐变（白 → 蓝）
    r = int(255 * (1 - progress))
    g = int(255 * (1 - progress))
    b = int(255 * progress)
    color = (r, g, b)

    # 绘制辐射状线条
    for i in range(line_count):
        angle = (i / line_count) * np.pi + rotation_angle  # 当前角度
        line_length = max_line_length * abs(np.sin(angle))  # 线长随角度变化

        # 起始点和终点
        start_x = CENTER_X + inner_radius * np.cos(angle)
        start_y = CENTER_Y + inner_radius * np.sin(angle)
        end_x = CENTER_X + (inner_radius + line_length) * np.cos(angle)
        end_y = CENTER_Y + (inner_radius + line_length) * np.sin(angle)

        # 绘制线条
        draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=2)

    return img

# ==============================
# 生成视频帧序列
# ==============================
frames_dir = "frames"
os.makedirs(frames_dir, exist_ok=True)
frame_paths = []

for i in range(FRAMES):
    t = i / FPS
    progress = get_t(t)
    rotation_angle = t * 0.5  # 缓慢旋转（弧度）
    frame_img = draw_dynamic_crescent(progress, rotation_angle)
    frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
    frame_img.save(frame_path)
    frame_paths.append(frame_path)
    print(f"Generated frame {i+1}/{FRAMES}")

# ==============================
# 合成为视频（使用 imageio）
# ==============================
output_video = "dynamic_crescent_animation.mp4"
with imageio.get_writer(output_video, fps=FPS) as writer:
    for frame_path in frame_paths:
        image = imageio.imread(frame_path)
        writer.append_data(image)

print(f"✅ 视频已保存为：{output_video}")