from setuptools import setup

setup(
    name='whatpulse',
    version='1.0.0',
    description='WhatPulse reverse engineered',
    url='https://github.com/sim642/whatpulse',
    author='Simmo Saan',
    author_email='simmo.saan@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    keywords='whatpulse module daemon evdev input network monitoring reverse-engineered',
    packages=[
        'whatpulse',
        'whatpulsed'
    ],
    install_requires=[
        'python-daemon',
        'evdev',
        'lxml',
        'requests'
    ],
    package_data={
        'whatpulse': [
            'whatpulse.pem'
        ]
    },
    entry_points={
        'console_scripts':[
            'whatpulsed=whatpulsed.whatpulsed:main',
            'whatpulse_upload=whatpulsed.upload_computerinfo:main'
        ]
    }
)
