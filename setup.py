import setuptools
from brs import brs


setuptools.setup(
    name='brs',
    version=brs.script_version,
    description='Post book data to Bruschetta web app.',
    author='takatoh',
    author_email='takatoh.m@gmail.com',
    packages=setuptools.find_packages(),
    install_requires=[
        'click',
        'PyYAML',
        'requests'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts':[
            'brs=brs.brs:main',
        ],
    }
)
