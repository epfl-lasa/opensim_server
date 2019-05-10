#!/usr/bin/env python

from setuptools import setup

setup(name='opensim_server',
      version='1.0',
      description='Opensim Server',
      author='Baptiste Busch',
      author_email='baptiste.busch@epfl.ch',
      packages=['opensim_server'],
      #scripts=['scripts/examples_animation.py', 'scripts/examples_vector_field.py'],
      package_dir={'': 'src'}
     )