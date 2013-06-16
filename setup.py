from setuptools import setup, find_packages
import os

version = '1.0~dev'

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).read()
changelog = open(os.path.join(base, 'CHANGELOG.rst')).read()

setup(name='docbucket',
      version=version,
      description='',
      long_description=readme + '\n' + changelog,
      classifiers=[],
      keywords='dms django',
      author='Antoine Millet',
      author_email='antoine@inaps.org',
      url='https://github.com/NaPs/Docbucket',
      license='MIT',
      data_files=(
          ('/etc/', ('etc/docbucket.conf',)),
      ),
      scripts=['docbucketadm'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[])
