# -*- coding: utf-8 -*-
"""Installer for the reflab.plone.importer package."""

from setuptools import find_packages
from setuptools import setup

setup(
    name = "reflab.plone.importer",
    version = "0.1",
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['reflab', 'reflab.plone'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        'setuptools',
        'plone.api>=1.8.4',
        'plone.app.dexterity',
    ],    
)