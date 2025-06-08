# Copyright (c) 2020, Yung-Yu Chen <yyc@solvcon.net>
# BSD-style license; see COPYING


import pathlib
import subprocess
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


# Taken from https://stackoverflow.com/a/48015772
class CMakeExtension(Extension):
    def __init__(self, name, **kwa):
        super().__init__(name, sources=[])


class cmake_build_ext(build_ext):
    user_options = build_ext.user_options + [
        ('cmake-args=', None, 'arguments to cmake'),
        ('make-args=', None, 'arguments to make'),
    ]

    def initialize_options(self):

        super().initialize_options()
        self.cmake_args = ''
        self.make_args = ''

    def finalize_options(self):

        super().finalize_options()

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):

        cwd = pathlib.Path().absolute()

        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name)).parent
        extdir.mkdir(parents=True, exist_ok=True)

        local_cmake_args = '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}'.format(
            str(extdir.absolute()))

        cmd = 'cmake {} {} {}'.format(cwd, local_cmake_args, self.cmake_args)
        proc = subprocess.run(cmd, shell=True, cwd=str(build_temp))
        if 0 != proc.returncode:
            raise RuntimeError('{} return {}'.format(cmd, proc.returncode))

        target_name = ext.name.split('.')[-1]
        cmd = 'make {} {}'.format(target_name, self.make_args)
        proc = subprocess.run(cmd, shell=True, cwd=str(build_temp))
        if 0 != proc.returncode:
            raise RuntimeError('{} return {}'.format(cmd, proc.returncode))


def main(is_py2app):
    setup_kwargs = dict(
        name="modmesh",
        version="0.0",
        packages=[
            'modmesh',
            'modmesh.onedim',
            'modmesh.pilot',
            'modmesh.pilot.airfoil',
            'modmesh.plot',
        ],
        setup_requires=['py2app'],
        cmdclass={'build_ext': cmake_build_ext},
        options={
            'py2app': {
                'argv_emulation': True,
                'iconfile': 'resources/pilot/solvcon.icns',
                'packages': ['modmesh', 'PySide6'],
                'excludes': ['PyInstaller', 'packaging', 'wheel'],
                'plist': {
                    'CFBundleName': 'modmesh',
                },
            }
        },
    )

    if is_py2app:
        setup_kwargs['app'] = ['modmesh.py']
        setup_kwargs['entry_points'] = {
            'console_scripts': [
                'modmesh=modmesh.pilot:launch',
            ],
        }
    else:
        setup_kwargs['ext_modules'] = [CMakeExtension('_modmesh')]

    setup(**setup_kwargs)

if __name__ == '__main__':
    is_py2app = 'py2app' in sys.argv
    main(is_py2app)

# vim: set ff=unix fenc=utf8 et sw=4 ts=4 sts=4:
