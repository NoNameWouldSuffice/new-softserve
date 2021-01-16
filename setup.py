from setuptools import setup, find_packages
setup(
name = "softserve",
version = "12.1.2",
description = "A python companion of the jackbord",
py_modules = ["softserve"],
author="Lachlan Paulsen",
packages = find_packages(exclude=["deps.*", "deps"]),
install_requires=["paho-mqtt==1.5.1"],
python_requires='>=3.6.7',
include_package_data=True
)
