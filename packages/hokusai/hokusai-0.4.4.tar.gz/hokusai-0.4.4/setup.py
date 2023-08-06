import os
from setuptools import setup

setup(name='hokusai',
      version=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hokusai', 'VERSION.txt'), 'r').read(),
      description='Artsy Docker development toolkit',
      url='http://github.com/artsy/hokusai',
      author='Isac Petruzzi',
      author_email='isac@artsymail.com',
      license='MIT',
      packages=['hokusai'],
      package_data={'hokusai': ['VERSION.txt', 'cli/*', 'commands/*', 'lib/*', 'services/*', 'templates/*']},
      install_requires=[
          'click==6.7',
          'click-repl==0.1.3',
          'MarkupSafe==1.0',
          'Jinja2==2.9.6',
          'PyYAML==3.12',
          'termcolor==1.1.0',
          'boto3==1.4.4',
          'botocore==1.5.41'
      ],
      zip_safe=False,
      include_package_data = True,
      scripts = ['bin/hokusai'])
