# syntax=docker/dockerfile:experimental
FROM python:3.7-slim-buster

RUN apt-get update && apt-get -y upgrade

# install git
RUN apt-get install -y git

# install ssh
RUN apt-get install -y openssh-client
RUN apt-get install -y ssh
# https://stackoverflow.com/questions/11618898/pg-config-executable-not-found
RUN apt-get install -y libpq-dev # for postgres driver
RUN apt-get install -y gcc

# config ssh to recognize github
# add ssh github's pub key to known host
RUN mkdir /root/.ssh && chmod 0700 /root/.ssh
RUN ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts
# use the following to test connections
# RUN --mount=type=ssh ssh -T git@github.com

ENV PIP_CACHE_DIR="/workspace/.pip"

# install project dependency
ADD requirements.txt requirements.txt
RUN --mount=type=ssh --mount=type=cache,target=/workspace/.pip pip install -r requirements.txt

# install dev dependency
RUN apt-get install -y curl
# install rust for the dev requirements
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
ADD dev_requirements.txt dev_requirements.txt
RUN --mount=type=ssh --mount=type=cache,target=/workspace/.pip pip install -r dev_requirements.txt

# deprecated.
ADD extra_requirements.txt extra_requirements.txt
RUN --mount=type=ssh --mount=type=cache,target=/workspace/.pip pip install -r extra_requirements.txt

# install external dependency
WORKDIR /external_dependencies
COPY ./external/ /external_dependencies
RUN cd gn5-client && python setup.py install

# add testing configuration
RUN mkdir -p ~/.aws
RUN echo "[default]" >> ~/.aws/config
RUN echo "region=eu-west-2" >> ~/.aws/config
RUN echo "output=json" >> ~/.aws/config

RUN echo "[default]" >> ~/.aws/credentials
RUN echo "aws_access_key_id=test" >> ~/.aws/credentials
RUN echo "aws_secret_access_key=test" >> ~/.aws/credentials

WORKDIR /workspace
CMD "bash"
