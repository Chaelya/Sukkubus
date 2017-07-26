#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 10:36:43 2017

@author: Chaelya
"""

from setuptools import setup

setup(name='funniest',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      #packages=['funniest'],
      install_requires=[
          'configparser',
          'requests',
          'PyQt5',
          'bbcode',
      ],
      zip_safe=False)