from setuptools import setup

NAME = "Minesweeper"

APP = ["minesweeper.py"]

DATA_FILES = [
    "resources"
]

OPTIONS = {
    "packages": ["pygame"],
    "iconfile": "resources/icon.icns"
}

setup(
    app = APP,
    name = NAME,
    data_files = DATA_FILES,
    options = {"py2app": OPTIONS},
    setup_requires = ["py2app"]
)
