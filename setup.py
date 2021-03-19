"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='azusa',
    version='0.1.4',
    description='Probability estimator for being on curve in mtg',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ihowell/azusa',
    author='Ian Howell',
    packages=['azusa'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        # 'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='mtg',
    python_requires='>=3.7, <4',
    install_requires=[
        'numpy',
        'requests',
        'terminaltables',
        'tqdm',
    ],
    extras_require={
        'tests': [
            'pytest',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/ihowell/azusa/issues',
        'Source': 'https://github.com/ihowell/azusa/',
    },
)
