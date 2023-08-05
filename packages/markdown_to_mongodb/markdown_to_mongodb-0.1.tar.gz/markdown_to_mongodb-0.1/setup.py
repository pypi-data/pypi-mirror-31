from setuptools import setup

setup(
    name='markdown_to_mongodb',
    version='0.1',
    packages=['markdown_to_mongodb'],
    url='http://www.github.com/ryanniebling',
    license='MIT',
    author='Ryan Niebling',
    author_email='nieblingr1@nku.edu',
    description='Converts a folder of markdown files and inserts them into a MongoDB instance.',
    install_requires=['pymongo']
)
