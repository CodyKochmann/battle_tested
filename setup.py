from distutils.core import setup

version = '2017.11.18.1',

setup(
  name = 'battle_tested',
  packages = ['battle_tested'], # this must be the same as the name above
  version = version,
  install_requires = ["hypothesis", "stricttuple", "prettytable", "generators", "strict_functions"],
  description = 'automated function and api fuzzer for easy testing of production code',
  author = 'Cody Kochmann',
  author_email = 'kochmanncody@gmail.com',
  url = 'https://github.com/CodyKochmann/battle_tested',
  download_url = 'https://github.com/CodyKochmann/battle_tested/tarball/{}'.format(version),
  keywords = ['battle_tested', 'test', 'hypothesis', 'fuzzing', 'fuzz', 'production', 'unittest', 'api', 'fuzzer', 'stress'],
  classifiers = [],
)
