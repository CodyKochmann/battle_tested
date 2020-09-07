from distutils.core import setup
from setuptools import find_packages


version = '2020.9.7.3'
package_name = 'battle_tested'
packages = find_packages()

assert package_name in packages, packages

setup(
  name = package_name,
  packages = packages,
  version = version,
  install_requires = ["hypothesis", "stricttuple", "prettytable", "generators", "strict_functions"],
  description = 'automated function and api fuzzer for easy testing of production code',
  author = 'Cody Kochmann',
  author_email = 'kochmanncody@gmail.com',
  url = 'https://github.com/CodyKochmann/battle_tested',
  download_url = f'https://github.com/CodyKochmann/battle_tested/tarball/{version}',
  keywords = ['battle_tested', 'test', 'hypothesis', 'fuzzing', 'fuzz', 'production', 'unittest', 'api', 'fuzzer', 'stress'],
  classifiers = []
)
