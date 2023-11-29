# -*- coding: utf-8 -*-

import glob
from setuptools import setup, find_packages

setup(
    name='py_chessboardjs',
    version='0.0.1',
    url='https://github.com/akuroiwa/py-chessboardjs',
    # # PyPI url
    # download_url='',
    license='GNU/GPLv3+',
    author='Akihiro Kuroiwa',
    author_email='akuroiwa@env-reform.com',
    description='Chess GUI using pywebview and chessboard.js.',
    # long_description="\n%s" % open('README.md').read(),
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    python_requires=">=3.7, !=3.10.*",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms='any',
    keywords=['evolutionary algorithms', 'genetic programming', 'gp', 'chess', 'fen', 'pgn'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pywebview', 'chess', 'chess-ant'],
    extras_require={
        # 'chess-ant': ['chess-ant'],
        'gtk': ['pywebview[gtk]'],
        'qt': ['pywebview[qt]'],
        'cef': ['pywebview[cef]']
    },
    entry_points={
        'console_scripts': [
            # 'py-chessboardjs = py_chessboardjs.start:run_gtk_gui',
            'py-chessboardjs-gtk = py_chessboardjs.start:run_gtk_gui',
            'py-chessboardjs-qt = py_chessboardjs.start:run_qt_gui',
            'py-chessboardjs-cef = py_chessboardjs.start:run_cef_gui'
            ]},
    # data_files=[
    #     ('', glob.glob('**/*.css', recursive=True)),
    #     ('', glob.glob('**/*.map', recursive=True)),
    #     ('', glob.glob('**/*.html', recursive=True)),
    #     ('', glob.glob('**/*.js', recursive=True)),
    #     ('', glob.glob('**/*.png', recursive=True))
    # ],
)
