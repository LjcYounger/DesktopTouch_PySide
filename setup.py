from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    name="img_utils",
    ext_modules=cythonize(
        "img_utils.pyx",
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False
        }
    ),
    include_dirs=[np.get_include()],
    extra_compile_args=["-fopenmp"],  # 启用OpenMP并行
    extra_link_args=["-fopenmp"]
)
