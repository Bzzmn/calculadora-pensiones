from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="pension-calculator",
    packages=find_packages(),
    ext_modules=cythonize([
        "calculator/pension_core.py"
    ], compiler_directives={
        'language_level': "3",
        'always_allow_keywords': True
    }),
    zip_safe=False
) 