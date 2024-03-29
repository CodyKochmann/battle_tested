# @Author: Cody Kochmann
# @Date:   2019-06-21 09:42:23
# @Last Modified by:   Marcin Pohl
# @Last Modified time: 2019-08-14 01:41:03

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-variables
MAKEFLAGS += --no-builtin-rules
SHELL := /bin/bash
.SHELLFLAGS := -u -o pipefail -c

### For testing only
GITTAGS_NEWEST := "2019.6.21.666"
### This uses GNU sort's 'version sorting' logic.  Git has its own sort routine, probably would be better.
GITTAGS_NEWEST = $(shell git tag -l | sort -Vr | head -n1)

### container references
CONTAINER_REGISTRY := "registry.gitlab.com/icody/containers"
DEBIAN := ${CONTAINER_REGISTRY}/debian:latest
ALPINE := ${CONTAINER_REGISTRY}/alpine:latest
PYTHON := ${CONTAINER_REGISTRY}/python:latest



TAG_FULL := $(GITTAGS_NEWEST)
TAG_YM   := $(shell echo $(TAG_FULL) | cut -d. -f1,2 )
TAG_D    := $(shell echo $(TAG_FULL) | cut -d. -f3 )
TAG_V    := $(shell echo $(TAG_FULL) | cut -d. -f4 )

ifeq ($(TAG_V),)
TAG_V := '.1'
else
### Using Bash's arithmetic context for natural numbers addition. Lets hope it can do this much.  If not, use AWK or bc.
TAG_V := $(shell echo .$$(( $(TAG_V) + 1 )) )
endif

TAG_NEXT = $(shell echo $(TAG_YM).$(TAG_D)$(TAG_V))

build:
	podman build .

podman-test-python:
	podman run -it --rm -v $(PWD):/outside ${PYTHON} sh -c 'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/__init__.py'

podman-test-alpine:
	podman run -it --rm -v $(PWD):/outside ${ALPINE} sh -c 'cp -rv /outside /inside && apk update && apk add python3 && python3 -m venv py3 && /py3/bin/pip install -r /inside/requirements.txt && cd /inside/battle_tested/ && /py3/bin/python __init__.py '

podman-test-debian:
	podman run -it --rm -v $(PWD):/outside ${DEBIAN} sh -c 'cp -rv /outside /inside && apt update && apt install -y python3 python3-venv && python3 -m venv py3 && cd inside && /py3/bin/pip install . && cd battle_tested && /py3/bin/python __init__.py'

beta-test-api-python:
	podman run -it --rm -v $(PWD):/outside ${PYTHON} sh -c	'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/beta/api.py'

beta-test-api-debian:
	podman run -it --rm -v $(PWD):/outside ${DEBIAN} sh -c 'cp -rv /outside /inside && apt update && apt install -y python3 python3-venv && python3 -m venv py3 && cd inside && /py3/bin/pip install . && /py3/bin/python api.py'

beta-test-runner-python:
	podman run -it --rm -v $(PWD):/outside ${PYTHON} sh -c	'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/beta/runner.py'

beta-test-runner-debian:
	podman run -it --rm -v $(PWD):/outside ${DEBIAN} sh -c 'cp -rv /outside /inside && apt update && apt install -y python3 python3-venv && python3 -m venv py3 && cd inside && /py3/bin/pip install . && /py3/bin/python runner.py'

beta-test-input_type_combos-python:
	podman run -it --rm -v $(PWD):/outside ${PYTHON} sh -c	'cp -rv /outside /inside && cd inside && pip install . && python battle_tested/beta/input_type_combos.py'

beta-test-input_type_combos-debian:
	podman run -it --rm -v $(PWD):/outside ${DEBIAN} sh -c 'cp -rv /outside /inside && apt update && apt install -y python3 python3-venv && python3 -m venv py3 && cd inside && /py3/bin/pip install . && /py3/bin/python input_type_combos.py'

podman-test-all: podman-test-python podman-test-alpine podman-test-debian

beta-test-all: beta-test-runner-python beta-test-api-python


test:
	@echo $(TAG_V)

gittag:
	@echo $(GITTAGS_NEWEST)

gittagnext:
	@echo $(TAG_NEXT)

### Not tested, you fix this one, just an outline
commit-update:
	git status
	#git add .
	#git commit
	#git push origin master
	#git tag $(TAG_NEXT) -m '{}'
	#git push --tags origin master
	#git status
