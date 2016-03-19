import vcversioner
from setuptools import setup


setup(
    name='pez',
    version=vcversioner.find_version().version,
    description='UINT dispenser as a service',
    long_description='',
    author='',
    author_email='',
    url='',
    classifiers=[],
    install_requires=[
        'falcon'
    ],
    test_suite='nose.collector',
    



)


