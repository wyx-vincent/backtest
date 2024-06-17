from setuptools import setup, find_packages

setup(
    name='backtest',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',
        'tqdm',
        'polygon-api-client'
    ]
)
