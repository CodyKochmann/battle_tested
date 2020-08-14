FROM python:latest
RUN pip install -U pip setuptools wheel

### make requirements.txt part of ./battle_tested/ so it all goes in one move instead of two?
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY ./battle_tested /battle_tested
WORKDIR /battle_tested

RUN echo 'running api.py...' && python api.py
RUN echo 'running runner.py...' && python runner.py
