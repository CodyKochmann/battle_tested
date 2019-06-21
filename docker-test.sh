# @Author: Cody Kochmann
# @Date:   2019-06-21 09:42:23
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2019-06-21 10:34:14

docker run -it --rm -v $(pwd):/outside python sh -c 'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/__init__.py'
exit
docker run -it --rm -v $(pwd):/outside alpine sh -c 'cp -rv /outside /inside && apk update && apk add python3 && python3 -m venv py3 && /py3/bin/pip install -r /inside/requirements.txt && cd /inside/battle_tested/ && /py3/bin/python __init__.py '

docker run -it --rm -v $(pwd):/outside debian sh -c 'cp -rv /outside /inside && apt update && apt install -y python3.5 python3.5-venv && python3.5 -m venv py3 && cd inside && /py3/bin/pip install . && cd battle_tested && /py3/bin/python __init__.py'
