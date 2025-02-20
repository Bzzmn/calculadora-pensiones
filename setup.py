from setuptools import setup, find_packages
from Cython.Build import cythonize

# Usar ruta relativa para pension_core.py
pension_core_path = "app/calculator/pension_core.py"

setup(
    name="pensionfi",
    version="0.1.0",
    packages=find_packages(include=['app', 'app.*']),
    ext_modules=cythonize([
        pension_core_path
    ], compiler_directives={
        'language_level': "3",
        'always_allow_keywords': True
    }),
    zip_safe=False,
) 