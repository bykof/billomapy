from distutils.core import setup

setup(
    name='billomapy',
    version='0.1',
    install_requires=open('requirements.txt').read().splitlines(),
    packages=['api'],
    url='https://github.com/bykof/billomapy',
    license='Apache License 2.0',
    author='mbykovski',
    author_email='mbykovski@seibert-media.net',
    description='A Python library for http://www.billomat.com/'
)
