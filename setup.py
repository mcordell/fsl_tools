#!/usr/bin/env python
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__),fname)).read()


setup(
        name='fsl_tools',
        description='FSL helper scripts',
        author='Michael Cordell',
        author_email='mcordell@mikecordell.com',
        long_description=read('README.md'),
        install_requires=[
            'xlrd',
            'xlwt',
            'xlutils'
            ],
        packages = ['fsl_tools'],
        entry_points = {
            'console_scripts': [
                'fsf_reporter = fsf_tools.fsf_reporter:main',
                ],   
        },

        
        
)
