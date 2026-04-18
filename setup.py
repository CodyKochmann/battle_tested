from setuptools import setup, find_packages

# Python version requirement for packaging metadata (needed for Python 3.13+)
python_requires = ">=3.9"

setup(
  name = 'battle_tested',
  packages = find_packages(),
  version = '2026.4.18',
  python_requires = python_requires,
  install_requires = ["hypothesis", "stricttuple", "prettytable", "generators", "strict_functions"],
  description = 'automated function and api fuzzer for easy testing of production code',
  long_description_content_type = 'text/markdown',
  author = 'Cody Kochmann',
  author_email = 'kochmanncody@gmail.com',
  url = 'https://github.com/CodyKochmann/battle_tested',
  keywords = ['battle_tested', 'test', 'hypothesis', 'fuzzing', 'fuzz', 'production', 'unittest', 'api', 'fuzzer', 'stress'],
  project_urls = {
    "Source": "https://github.com/CodyKochmann/battle_tested"
  },
  classifiers = [
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.9',
      'Programming Language :: Python :: 3.10',
      'Programming Language :: Python :: 3.11',
      'Programming Language :: Python :: 3.12',
      'Programming Language :: Python :: 3.13',
      'Programming Language :: Python :: 3.14',
      'Topic :: Software Development :: Testing',
  ],
)
