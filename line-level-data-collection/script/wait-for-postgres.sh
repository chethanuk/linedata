#!/bin/sh

pg_isready -d dlp -h localhost -U dlpUser -t 10
while [ $? -ne 0 ]; do
    pg_isready -d dlp -h localhost -U dlpUser -t 10
done