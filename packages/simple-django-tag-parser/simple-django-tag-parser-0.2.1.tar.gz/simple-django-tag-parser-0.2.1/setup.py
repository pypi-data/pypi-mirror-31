# coding=utf-8

from setuptools import find_packages, setup
import pathlib
import os

MAIN_DIR = pathlib.Path(__file__).absolute().parent

packages = find_packages(
  str(MAIN_DIR),
  include=('django_tag_parser*',),
  exclude=[]
)

# Did I mention that setup.py is not finest piece of software on earth.
# For this to work when installed you'll need to enumerate all template and static file.


def read_dir(package: str, directory: str):
  package_root = os.path.abspath(package.replace(".", "/"))
  directory = os.path.join(package_root, directory)
  res = []
  for root, subFolders, files in os.walk(directory):
    for file in files:
      res.append(
        os.path.relpath(
         os.path.join(root, file),
         package_root
        ))

  return res


if __name__ == "__main__":

  setup(
    name='simple-django-tag-parser',
    version='0.2.1',
    packages=packages,
    license='MIT',
    author='Jacek Bzdak',
    author_email='jacek@askesis.pl',
    description='Simple helper to make developing new django tags easier.',
    include_package_data=True
  )
