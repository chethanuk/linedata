#!/bin/bash
set -e

aws s3 sync s3://lldc-qa-corpus-bucket20230208073512051600000001 ./corpus
aws s3 sync ./corpus s3://lldc-production-corpus-bucket20230208082134035300000001