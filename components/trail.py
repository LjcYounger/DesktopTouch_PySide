import pygame as pg
import math
import numpy as np

class Trail(pg.sprite.Sprite):
    """
    拖尾特效类
    
    创建跟随鼠标移动的拖尾视觉效果，通过一系列渐变透明的图像切片
    来模拟运动轨迹的拖尾效果。
    """
    
    def __init__(self, speed, allsize, tps, screensize, tp_size):
        """
        初始化拖尾特效
        
        Args:
            speed (float): 动画播放速度
            allsize (float): 基准尺寸
            tps (list): 拖尾图案切片列表
            screensize (tuple): 屏幕尺寸 (width, height)
            tp_size (tuple): 单个切片的尺寸 (width, height)
        """
        super().__init__()
        
        # 基本属性
        self.type = "trail"  # 精灵类型标识
        self.life = 0.3      # 拖尾生命周期
        self.size = 0.12 * allsize  # 基准尺寸
        self.screensize = screensize  # 屏幕尺寸
        self.image = pg.Surface(self.screensize, pg.SRCALPHA)  # 创建透明绘图表面
        self.rect = self.image.get_rect(topleft=(0, 0))  # 设置位置
        
        # 计算切片间隔和重新排列切片
        self.dn = tp_size[0] / (speed * self.life)  # 每帧的切片步长
        self.tps = [tps[int(i)] for i in np.arange(0, len(tps), self.dn)]  # 重新采样切片
        self.tps.reverse()  # 反转顺序使最新的在最前面
        self.trails = [None] * len(self.tps)  # 存储拖尾序列
        self.die = 0      # 销毁计数器
        self.live = True  # 生存状态标志

    def update(self, **kwargs):
        """
        更新拖尾特效状态
        
        Args:
            **kwargs: 包含鼠标位置和状态信息的字典
                     - previous_pos: 上一帧鼠标位置
                     - mouse_pos: 当前鼠标位置  
                     - delta_pos: 位置变化向量
                     - distance: 移动距离
                     - mouse_pressed: 鼠标是否按下
        """
        # 获取鼠标位置信息
        previous_pos, mouse_pos = kwargs["previous_pos"], kwargs["mouse_pos"]
        if previous_pos and mouse_pos:
            # 提取其他必要参数
            delta_pos = kwargs["delta_pos"]
            distance = kwargs["distance"]
            mouse_pressed = kwargs["mouse_pressed"]

            # 清空绘图表面
            self.image.fill((0, 0, 0, 0))

            # 如果还处于活跃状态，添加新的拖尾元素
            if self.live:
                # 计算拖尾角度
                angle = math.degrees(math.atan2(delta_pos[0], delta_pos[1]))
                # 创建旋转和缩放后的切片序列
                slis = [pg.transform.rotate(pg.transform.scale(ix, (ix.get_size()[0], distance)), angle) for ix in self.tps]
                # 计算中点位置
                apos = tuple((x1 + x2) / 2 for x1, x2 in zip(previous_pos, mouse_pos))
                # 添加到拖尾序列
                self.trails.append([slis, apos])
            
            # 维护拖尾序列长度
            if len(self.trails) >= len(self.tps) or not self.live and self.trails:
                self.trails.pop(0)  # 移除最早的元素
            
            # 绘制所有拖尾元素
            for index, sli in enumerate(self.trails):
                if sli:
                    # 获取对应索引的图像切片
                    image = sli[0][index]
                    # 设置透明度（越旧的元素越透明）
                    image.set_alpha(255 * index / len(self.trails))
                    # 绘制到主表面
                    self.image.blit(image, (sli[1][0] - image.get_size()[0] / 2, sli[1][1] - image.get_size()[1] / 2))
            
            # 发光效果（被注释）
            # self.image = apply_glow_effect(self.image, 10, 10)
            
            # 更新生存状态
            if not mouse_pressed:
                self.live = False  # 鼠标释放后停止添加新元素
            
            # 处理销毁逻辑
            if not self.live:
                if self.die > len(self.tps):
                    self.kill()  # 所有拖尾元素消失后销毁精灵
                self.die += 1  # 增加销毁计数