#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    "dnspython",
    "docopt>=0.6",
    "tldextract",
    "xn_twist_python_sdk"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='xn-twist',
    version='1.4.0',
    description="Unicode Domain-Squat Finder",
    long_description=readme,
    author="Floyd Hightower",
    author_email='',
    url='https://github.com/xn-twist/xn-twist',
    packages=[
        'xn_twist',
    ],
    entry_points={
        'console_scripts': [
            'xntwist=xn_twist.cli:main'
        ]
    },
    package_dir={'xn_twist':
                 'xn_twist'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='xn_twist',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
