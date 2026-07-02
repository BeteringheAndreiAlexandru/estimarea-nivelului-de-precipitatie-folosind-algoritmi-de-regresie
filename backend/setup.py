from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "custom_rf",
        ["random_forest.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
    ),
]

setup(
    name="custom_rf",
    version="1.0",
    description="Modul Random Forest in C++",
    ext_modules=ext_modules,
)