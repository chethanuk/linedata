# syntax=docker/dockerfile:experimental
# docker file for using the aws cli
FROM amazon/aws-cli

RUN mkdir -p ~/.aws
RUN echo "[default]" >> ~/.aws/config
RUN echo "region=eu-west-2" >> ~/.aws/config
RUN echo "output=json" >> ~/.aws/config

RUN echo "[default]" >> ~/.aws/credentials
RUN echo "aws_access_key_id=test" >> ~/.aws/credentials
RUN echo "aws_secret_access_key=test" >> ~/.aws/credentials

WORKDIR /workspace
ENTRYPOINT []
CMD "bash"