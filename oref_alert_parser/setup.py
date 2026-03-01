from setuptools import setup, find_packages

setup(
    name='oref_alert_parser',
    version='0.1.0',
    packages=find_packages(),
    description='A package to parse alerts from the Home Front Command (Oref)',
    author='Tohar Laufer',
    author_email='tohar@example.com',
    url='https://github.com/tohar65/quiet_alert',
    install_requires=[
        'requests',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'oref-alert-parser=oref_alert_parser.main:main',
            'update-locations=oref_alert_parser.locations_updater:main',
        ],
    },
)
