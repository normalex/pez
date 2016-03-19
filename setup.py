import vcversioner
from setuptools import setup, find_packages


dev_requirements=[
    'nose',
    'nose-parameterized',
    'mock',
    'coverage',
    'fabric',
    'fabtools',
    'boom',
    'WebTest>=2.0.16'
]

setup(
    name='pez',
    version=vcversioner.find_version(
        version_module_paths=['pez/version.py'],
        fallback_version='v0.0.0-0-dev'
    ).version,
    description='Numbers dispenser as a service',
    long_description='Generates sequential unique 64 bit unsigned integers',
    author='anormuradov',
    author_email='normalex@gmail.com',
    url='https://github.com/normalex/pez',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'falcon>=0.3.0',
        'sqlalchemy',
        'pg8000',
        'gunicorn'
    ],
    tests_require=dev_requirements,
    test_suite='nose.collector',
    extras_require={'test': dev_requirements},  # to make life easier
)


