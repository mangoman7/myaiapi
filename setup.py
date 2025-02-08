from setuptools import setup, find_packages

setup(
    name='myaiapi',
    version='0.0.0.3',
    packages=find_packages(),
    install_requires=[
        "requests",
        "flask"
    ],
)
