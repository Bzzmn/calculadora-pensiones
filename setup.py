from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "calculator.pension_core",
        ["calculator/pension.py"],
        include_dirs=[numpy.get_include()]
    )
]

setup(
    name="pension-calculator",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
    })
) 