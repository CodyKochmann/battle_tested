# @Author: Cody Kochmann
# @Date:   2019-06-21 09:42:23
# @Last Modified by:   Cody Kochmann
# @Last Modified time: 2019-06-21 11:27:03

SHELL := /bin/bash

docker-test-python:
	docker run -it --rm -v $(PWD):/outside python sh -c 'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/__init__.py'

docker-test-alpine:
	docker run -it --rm -v $(PWD):/outside alpine sh -c 'cp -rv /outside /inside && apk update && apk add python3 && python3 -m venv py3 && /py3/bin/pip install -r /inside/requirements.txt && cd /inside/battle_tested/ && /py3/bin/python __init__.py '

docker-test-debian:
	docker run -it --rm -v $(PWD):/outside debian sh -c 'cp -rv /outside /inside && apt update && apt install -y python3.5 python3.5-venv && python3.5 -m venv py3 && cd inside && /py3/bin/pip install . && cd battle_tested && /py3/bin/python __init__.py'

beta-test-api-python:
	docker run -it --rm -v $(PWD):/outside python sh -c	'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/api.py'

beta-test-runner-python:
	docker run -it --rm -v $(PWD):/outside python sh -c	'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/runner.py'

docker-test-all:
	$(MAKE) docker-test-python
	$(MAKE) docker-test-alpine
	$(MAKE) docker-test-debian

beta-test-all:
	$(MAKE) beta-test-runner-python
	$(MAKE) beta-test-api-python
