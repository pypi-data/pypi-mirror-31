# coding: utf-8

from setuptools import setup

setup(
    name='mlang',
    version='0.1.9',
    packages=['mlang.res', 'mlang_client'],
    py_modules=['mlang.config', 'mlang.utils'],
    url='',
    license='MIT',
    author='lishouguang',
    author_email='lishouguang@meizu.com',
    description='mlang client',
    long_description='# xx',
    long_description_content_type='text/markdown',
    install_requires=['progressbar2', 'requests-toolbelt', 'numpy', 'cachetools']
)
