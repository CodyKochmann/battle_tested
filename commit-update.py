from os import popen, chdir
from datetime import datetime

chdir("/Users/cody/git/battle_tested/")

def bash(command, check=True):
    if check:
        raw_input('about to run: {} [enter to continue]'.format(command))
    return popen(command).read()

def list_tags():
    ''' returns a list of the tags in the repo '''
    return bash('git tag -l', False).strip().split('\n')

def latest_tag():
    """ returns the latest tag used """
    out = ''
    tags_all_sorted = sorted(list_tags())
    if tags_all_sorted is not None:
        out = tags_all_sorted[-1]
    return out

def create_next_tag():
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

def replace_all_in_file(file_path, old, new):
    with open(file_path, 'r') as reader:
        file_text = reader.read()
    file_text = file_text.replace(old, new)
    with open(file_path, 'w') as writer:
        writer.write(file_text)

def update_setup():
    args = 'setup.py', latest_tag(), create_next_tag()
    raw_input("about to replace {1:} with {2:} in {0:}".format(*args))
    replace_all_in_file(*args)

def sync_readmes():
    """ just copies README.md into README for pypi documentation """
    print("syncing README")
    with open("README.md", 'r') as reader:
        file_text = reader.read()
    with open("README", 'w') as writer:
        writer.write(file_text)


# make this part automated later, Im tired...
update_setup()
sync_readmes()

commit_message = raw_input('Enter your commit message: ')

bash("git status", False)
bash('git add .')
bash("git commit -m '{}'".format(commit_message))
bash("git push origin master")
bash("git tag {} -m '{}'".format(create_next_tag(), commit_message))
bash("git push --tags origin master")
bash("git status", False)
#bash("python setup.py register -r pypitest")
bash("python setup.py sdist upload -r pypitest")
#bash("python setup.py register -r pypi")
bash("python setup.py sdist upload -r pypi")
