from setuptools import setup, find_packages

setup(
    name='Easy-Pixie',
    version='0.0.1',
    author='Floating Ocean',
    author_email='sea113290980@gmail.com',
    license='MIT',
    packages=['easy_pixie'],
    description='A tool to simplify the use of python graphic library pixie-python.',
    install_requires=[
        'pixie-python>=4.3.0'
    ]
)
