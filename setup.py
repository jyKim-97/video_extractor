from setuptools import setup, find_packages
from pathlib import Path
import re


def find_version():
    init_path = Path(__file__).parent / "video_extractor" / "__init__.py"
    match = re.search(r'^__version__ = ["\']([^"\']+)["\']', init_path.read_text(), re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Cannot find version in __init__.py")


def setup_package():
    setup(
        name="video_extractor",
        version=find_version(),
        author="jungyoung",
        description="A package for extracting video data",
        packages=find_packages(),
        python_requires=">=3.10",
        install_requires=[
            "pyqt5",
            "tqdm",
            "opencv-python",
            "pytesseract" 
            # Need to install tesseract: https://github.com/UB-Mannheim/tesseract/wiki
            # (Window) Add installed directory to the environment variable
        ],
        entry_points={
            "console_scripts": [
                "extract_video = video_extractor.__main__:main"
            ],
        },
    )

    
if __name__ == "__main__":
    setup_package()