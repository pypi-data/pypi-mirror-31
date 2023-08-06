from setuptools import find_packages, setup
setup(
name = 'amdataset',
version = '0.1.1',
packages = find_packages(),
author = 'Ammad Khalid',
description = 'Simple Database CRUD Package Using databaset Package',
long_description = open('README.md', 'r').read(),
install_requires = ['dataset'],
keywords = 'database,dataset,ORM',
url = 'https://github.com/Ammadkhalid/am-dataset.git',
author_email = 'Ammadkhalid12@gmail.com'
)
