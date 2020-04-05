from distutils.core import setup

setup(
  name = 'battle_tested',
  packages = ['battle_tested'], # this must be the same as the name above
  version = '2019.6.21',
  install_requires = ["hypothesis", "stricttuple", "prettytable", "generators", "strict_functions"],
  description = 'automated function and api fuzzer for easy testing of production code',
  author = 'Cody Kochmann',
  author_email = 'kochmanncody@gmail.com',
  url = 'https://github.com/CodyKochmann/battle_tested',
  download_url = 'https://github.com/CodyKochmann/battle_tested/tarball/2019.6.21',
  keywords = ['battle_tested', 'test', 'hypothesis', 'fuzzing', 'fuzz', 'production', 'unittest', 'api', 'fuzzer', 'stress'],
  classifiers = [],
)
