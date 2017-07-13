def walk(dir='./'):
  '''hello'''
  print('running walk')
  scan_queue=[ls(dir)]
  out=[]
  while len(scan_queue):
    # pop the next item to scan
    for i in scan_queue.pop():
      # yield its path
      out.append(i.path)
      # if directory, add it to the queue
      if i.is_dir():
        scan_queue.append(ls(i.path))
  return out





















def walk(dir='./'):                    | walk - <function walk at 0x10eea9378>
                                       | dir  - './'
  '''hello'''
  print('running walk')                | print - <built-in function print>
  scan_queue=[ls(dir)]                 | scan_queue - []
                                       | ls  - <built-in function scandir>
                                       | dir - './'
  out=[]                               | out - []
  while len(scan_queue):               | scan_queue - {['./.hypothesis',
                                       |     './__init__.py',
                                       |     './__init__.pyc',
                                       |     './__pycache__',
                                       |     './dis_list.py',
                                       |     './inject_frames.py',
                                       |     './__pycache__/__init__.cpython-36.pyc',
                                       |     './__pycache__/dis_list.cpython-36.pyc',
                                       |     './__pycache__/feeler.cpython-36.pyc',
                                       |     './__pycache__/loaded_modules.cpython-36.pyc',
                                       |     './.hypothesis/examples',
                                       |     './.hypothesis/tmp',
                                       |     './.hypothesis/unicodedata',
                                       |     './.hypothesis/unicodedata/5.2.0',
                                       |     './.hypothesis/unicodedata/9.0.0',
                                       |     './.hypothesis/unicodedata/9.0.0/charmap.pickle.gz',
                                       |     './.hypothesis/unicodedata/5.2.0/charmap.pickle.gz',
                                       |     './.hypothesis/examples/3282948af17dd9e9',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e',
                                       |     './.hypothesis/examples/eea47f2c4f2b9fb6',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e/1489f923c4dca729',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e/4a9071560e3a5a52']}
    for i in scan_queue.pop():         | i - <DirEntry '4a9071560e3a5a52'>
      out.append(i.path)               | out - ['./.hypothesis',
                                       |     './__init__.py',
                                       |     './__init__.pyc',
                                       |     './__pycache__',
                                       |     './dis_list.py',
                                       |     './inject_frames.py',
                                       |     './__pycache__/__init__.cpython-36.pyc',
                                       |     './__pycache__/dis_list.cpython-36.pyc',
                                       |     './__pycache__/feeler.cpython-36.pyc',
                                       |     './__pycache__/loaded_modules.cpython-36.pyc',
                                       |     './.hypothesis/examples',
                                       |     './.hypothesis/tmp',
                                       |     './.hypothesis/unicodedata',
                                       |     './.hypothesis/unicodedata/5.2.0',
                                       |     './.hypothesis/unicodedata/9.0.0',
                                       |     './.hypothesis/unicodedata/9.0.0/charmap.pickle.gz',
                                       |     './.hypothesis/unicodedata/5.2.0/charmap.pickle.gz',
                                       |     './.hypothesis/examples/3282948af17dd9e9',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e',
                                       |     './.hypothesis/examples/eea47f2c4f2b9fb6',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e/1489f923c4dca729',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e/4a9071560e3a5a52']
                                       | scan_queue - []
      if i.is_dir():                   | i - <DirEntry '4a9071560e3a5a52'>
        scan_queue.append(ls(i.path))  | ls - <built-in function scandir>
    return out                         | out - ['./.hypothesis',
                                       |     './__init__.py',
                                       |     './__init__.pyc',
                                       |     './__pycache__',
                                       |     './dis_list.py',
                                       |     './inject_frames.py',
                                       |     './__pycache__/__init__.cpython-36.pyc',
                                       |     './__pycache__/dis_list.cpython-36.pyc',
                                       |     './__pycache__/feeler.cpython-36.pyc',
                                       |     './__pycache__/loaded_modules.cpython-36.pyc',
                                       |     './.hypothesis/examples',
                                       |     './.hypothesis/tmp',
                                       |     './.hypothesis/unicodedata',
                                       |     './.hypothesis/unicodedata/5.2.0',
                                       |     './.hypothesis/unicodedata/9.0.0',
                                       |     './.hypothesis/unicodedata/9.0.0/charmap.pickle.gz',
                                       |     './.hypothesis/unicodedata/5.2.0/charmap.pickle.gz',
                                       |     './.hypothesis/examples/3282948af17dd9e9',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e',
                                       |     './.hypothesis/examples/eea47f2c4f2b9fb6',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e/1489f923c4dca729',
                                       |     './.hypothesis/examples/a7208dfe3ff4435e/4a9071560e3a5a52']
