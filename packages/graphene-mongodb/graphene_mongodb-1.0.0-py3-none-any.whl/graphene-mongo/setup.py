from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='graphene-mongo',
  packages=['graphene-mongo'],
  version='1.0.0',
  description='GrapheneMongo is a library that integrates Graphene with MongoEngine',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='João Vitor Silvestre',
  author_email='joaovitorsilvestresousa@gmail.com',
  url='https://github.com/joaovitorsilvestre/graphene-mongo',
  download_url='https://github.com/joaovitorsilvestre/graphene-mongo/archive/1.0.tar.gz',
  keywords=['graphene', 'graphql', 'mongo', 'mongodb', 'mongoDB', 'mongoengine'],
  classifiers=[],
  install_requires=[
    'aniso8601>=3.0.0',
    'appdirs>=1.4.3',
    'graphene>=2.1',
    'graphql-core>=2.0',
    'graphql-relay>=0.4.5',
    'iso8601>=0.1.12',
    'mongoengine>=0.15.0',
    'promise>=2.1',
    'pymongo>=3.6.1',
    'pyparsing>=2.2.0',
    'rx>=1.6.1',
    'six>=1.11.0',
    'typing>=3.6.4'
  ]
)