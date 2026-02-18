from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt

from img_utils import change_image_by_grayscale
from constants import GlobalConstants, RingConstants

def generate_animated_frame(time, Constants, grayscale_image_transparent=False) -> QPixmap | None:
        """
        根据时间生成当前帧的QPixmap
        """
        time_percentage = time / Constants.START_LIFETIME
        # 限制时间范围在0-1之间
        if time_percentage < 0.0 or time_percentage > 1.0:
            return None
        
        # 使用推导式一次性计算RGB颜色值
        rgb_values = tuple(
            int(max(0, min(255, Constants.COLOR_OVER_LIFETIME[i](time_percentage))))
            for i in range(3)  # r, g, b三个通道
        )
        
        # 获取alpha值
        alpha_value = int(max(0, min(255, Constants.COLOR_OVER_LIFETIME[3](time_percentage))))
        
        # 计算尺寸缩放因子
        size_multiplier = float(Constants.SIZE_OVER_LIFETIME(time_percentage))
        
        # 计算实际尺寸
        actual_size = max(1, int(GlobalConstants.SIZE * Constants.START_SIZE * size_multiplier))  # 确保至少为1像素
        
        # 应用颜色和透明度变换
        result_pixmap = change_image_by_grayscale(
            Constants.GRAYSCALE_IMAGE,
            rgb_values,
            alpha_value,
            grayscale_image_transparent
        )
        
        # 创建变换对象
        transform = QTransform()
        
        # 应用缩放变换
        #transform.scale(size_multiplier, size_multiplier)
        
        # 应用旋转变换
        transform.rotate(Constants.ROTATION_OVER_LIFETIME(time_percentage))
        #if Constants.ROTATION_OVER_LIFETIME(time_percentage) != 0:
        #    print(Constants.ROTATION_OVER_LIFETIME(time_percentage))
        
        # 应用变换到pixmap
        transformed_pixmap = result_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        
        # 调整最终尺寸
        final_pixmap = transformed_pixmap.scaled(
            actual_size, actual_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )

        return final_pixmap