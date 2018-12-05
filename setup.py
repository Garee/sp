#!/usr/bin/env python3

import re
import setuptools

with open('sp/sp.py') as f:
    VERSION = re.search(r'_VERSION_ = "(.*?)"', f.read()).group(1)

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    name='spcli',
    version=VERSION,
    url='https://github.com/garee/sp',
    license='GPLv3',
    author='Gary Blackwood',
    author_email='gary@garyblackwood.co.uk',
    description='Search Startpage.com from the terminal.',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires='>=3.4',
    platforms=['any'],
    py_modules=['sp/sp'],
    entry_points={
        'console_scripts': [
            'sp = sp:main',
        ],
    },
    install_requires=[
        'colorama>=0.4.1',
        'lxml>=4.2.5',
        'pyperclip>=1.7.0',
        'requests>=2.20.1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities'
    ]
)
