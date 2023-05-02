# syntax=docker/dockerfile:experimental
ARG FUNCTION_DIR="/home/app/"
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

ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}
# install project dependency
ADD requirements.txt requirements.txt
RUN --mount=type=ssh --mount=type=cache,target=/workspace/.pip pip install -r requirements.txt

# install awslambdaric as it is required by AWS
RUN --mount=type=ssh --mount=type=cache,target=/workspace/.pip pip install awslambdaric
COPY release/entry.sh ${FUNCTION_DIR}
RUN chmod 755 ${FUNCTION_DIR}/entry.sh

# install external dependency
WORKDIR /external_dependencies
COPY ../external /external_dependencies
RUN cd gn5-client && python setup.py install
WORKDIR ${FUNCTION_DIR}

# install this project
COPY line_level_data_collection line_level_data_collection
COPY setup.py setup.py
RUN python setup.py install

# Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
# `/usr/bin/aws-lambda-rie` MUST match the path in entry.sh
# reference: https://github.com/aws/aws-lambda-runtime-interface-emulator#how-to-configure
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

ENTRYPOINT [ "/home/app/entry.sh" ]
# doesn't matter too much as it will be overriden in lambda config
CMD [ "line_level_data_collection/consolidate_handler.consolidate_data" ]