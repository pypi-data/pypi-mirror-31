# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='colorscale',
      version = '0.8.0',
      description = 'Python package to convert images from grayscale to false color and back',
      long_description = '',
      author = 'Philipp Klaus',
      author_email = 'philipp.l.klaus@web.de',
      url = 'https://github.com/pklaus/python_colorscale',
      license = 'GPL',
      packages = ['colorscale'],
      entry_points = {
          'console_scripts': [
              'to_color_scale = colorscale.to_color_scale:main',
              'to_gray_scale  = colorscale.to_gray_scale:main',
          ],
      },
      include_package_data = False,
      zip_safe = True,
      platforms = 'any',
      install_requires = [
          "pillow>=3.3.0",
          "opencv-python",
          "numpy",
      ],
      keywords = 'False color colorscale colormap color map',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Visualization',
      ]
)

