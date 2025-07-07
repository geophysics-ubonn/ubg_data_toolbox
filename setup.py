#!/usr/bin/env python3
import os
from glob import glob
from setuptools import setup

version_short = '0.2'
version_long = '0.2.4'

extra = {}

# generate entry points and scripts
entry_points = {'console_scripts': []}
scripts = [os.path.basename(script)[0:-3] for script in glob('src/*.py')]

for script in scripts:
    print(script)
    entry_points['console_scripts'].append(
        '{0} = {0}:main'.format(script)
    )

if __name__ == '__main__':
    setup(
        name='ubg_data_toolbox',
        version=version_long,
        description='',
        author='Maximilian Weigand',
        author_email='mweigand@geo.uni-bonn.de',
        package_dir={
            '': 'src',
            'ubg_data_toolbox': 'lib/ubg_data_toolbox',
        },
        packages=[
            'ubg_data_toolbox',
            'ubg_data_toolbox.checks',
        ],
        entry_points=entry_points,
        py_modules=scripts,
        install_requires=[
            'numpy',
            'ipython',
            'prompt_toolkit',
            'pandas',
        ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 3.4",
            "Intended Audience :: Science/Research",
        ],
        **extra
    )
