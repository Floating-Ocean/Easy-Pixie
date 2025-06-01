"""
pip包信息
"""

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(name="Easy-Pixie",
                 version="0.0.7",
                 author="Floating Ocean",
                 author_email="sea113290980@gmail.com",
                 description="A tool to simplify the use of python graphic library pixie-python.",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/Floating-Ocean",
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 python_requires='>=3.10.0',
                 packages=setuptools.find_namespace_packages(
                     include=["easy_pixie"], ),
                 install_requires=['pixie-python>=4.3.0'],
                 include_package_data=True)
