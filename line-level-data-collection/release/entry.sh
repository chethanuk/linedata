#!/bin/sh
# -z string True if the string is null
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
  # using the emulator to test locally
  # make sure python is available in this path
  exec /usr/bin/aws-lambda-rie /usr/local/bin/python -m awslambdaric $1
else
  # this is supposed to be run on aws lambda
  # make sure python is available in this path
  exec /usr/local/bin/python -m awslambdaric $1
fi
