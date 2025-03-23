from setuptools import setup, find_packages

setup(
    name="green_elevator_bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aiogram",
        "python-dotenv",
        "colorama",
        "pytest",
        "pytest-asyncio"
    ],
) 