from setuptools import setup

setup(
    name='billomapy',
    version='2.5.1',
    install_requires=['requests==2.7.0', 'tornado==4.2'],
    packages=['billomapy'],
    url='https://github.com/bykof/billomapy',
    license='Apache License 2.0',
    author='Michael Bykovski',
    author_email='mbykovski@seibert-media.net',
    description='A Python library for http://www.billomat.com/'
)
