from setuptools import setup, find_packages

setup(
    name="dhl-label-cropper",
    version="3.0.0",
    author="DYAI",
    description="Robust DHL Label Cropper with Anti-Freeze Protection",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DYAI2025/Label_chopper",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF==1.23.8",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dhl-cropper=src.START_CROPPER:install_and_run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
