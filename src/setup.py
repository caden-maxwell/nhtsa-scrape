import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "excludes": ["tkinter", "unittest", "asyncio"],
    "zip_include_packages": ["requests", "PyQt6", "beautifulsoup4"],
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="NHTSA Scrape Tool",
    version="1.0",
    description="GUI App for NHTSA Scrape",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
