#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    name='ShapKa',
    version='1.1.1',
    author="Ayhan UYANIK",
    author_email='uyanik.ayhan@gmail.com',
    description="Key Satisfaction Drivers Analysis based on Shapley values and Kano model",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst', 
    url='https://github.com/auyanik/ShapKa',
    packages=find_packages(),
    #scripts=["ShapKa/kanomodel.py", "ShapKa/cooperativegame.py", "ShapKa/payoff.py"],
    python_requires='>=3.7.*',
    license="MIT license",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Development Status :: 5 - Production/Stable',
    ],
    install_requires=requirements,
    include_package_data=True,
    keywords='ShapKa',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False,
)
