from os import popen, chdir
from datetime import datetime

chdir("/Users/cody/git/battle_tested/")

def bash(command, check=True):
    if check:
        raw_input('about to run: {} [enter to continue]'.format(command))
    return popen(command).read()

def list_tags():
    ''' returns a list of the tags in the repo '''
    return bash('git tag', False).strip().split('\n')

def next_tag():
    ''' returns the next tag that will be used '''

def latest_tag():
    """ returns the latest tag used """
    out = ''
    for i in sorted(list_tags()):
        out = i
    return out

def create_tag():
    """ creates a tag based on the date and previous tags """
    date = datetime.utcnow()
    date_tag = '{}.{}.{}'.format(date.year, date.month, date.day)
    if date_tag in latest_tag(): # if there was an update already today
        latest = latest_tag().split('.') # split by spaces
        if len(latest) == 4: # if it is not the first revision of the day
            latest[-1]= str(int(latest[-1])+1)
        else: # if it is the first revision of the day
            latest+=['1']
        date_tag = '.'.join(latest)
    return date_tag

commit_message = raw_input('Enter your commit message: ')

bash("git status", False)
bash('git add .')
bash("git commit -m '{}'".format(commit_message))
bash("git push origin master")
bash("git tag {} -m '{}'".format(create_tag(), commit_message))
bash("git push --tags origin master")
bash("git status", False)
bash("python setup.py register -r pypitest")
bash("python setup.py sdist upload -r pypitest")
bash("python setup.py register -r pypi")
bash("python setup.py sdist upload -r pypi")
