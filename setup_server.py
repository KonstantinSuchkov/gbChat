import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["log"],
    "includes": ['sqlalchemy', 'sqlite3', '_sqlite3'],
    'include_msvcr': True,
}

executables = [Executable('server.py', base='Win32GUI'),
               Executable('client.py', base='Win32GUI'),
               ]

setup(
    name="chat_server",
    version="0.0.1",
    description="chat_server",
    options={
        "build_exe": build_exe_options
    },
    executables=executables
)
