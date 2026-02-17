from PySide6.QtGui import QPixmap, QPainter

from constants import RingXConstants
from generate_frame import generate_animated_frame

class RingX:
    """
    扩展环形特效类
    """
    START_SIZE = RingXConstants.get_start_size()
    