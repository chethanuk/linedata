import gzip
import json
import os
import tempfile
from pathlib import Path
from typing import Union, List, Dict

import boto3
import botocore

JSON = Union[Dict[str, "JSON"], List["JSON"], str, int, float, bool, None]


# https://stackoverflow.com/a/63017309
# need s3:Listobject permission to do head_object
def download_s3_file(client, bucket: str, key: str, absolute_path: str) -> bool:
    try:
        _ = client.head_object(Bucket=bucket, Key=key)
        _ = client.download_file(Bucket=bucket, Key=key, Filename=absolute_path)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == '404':
            return False
        else:
            raise e


def download_s3_file_and_load_content(client, bucket: str, key: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp_dirname:
        file_path = Path(tmp_dirname) / "temp.json"
        is_successful = download_s3_file(client, bucket, key, str(file_path))
        if is_successful:
            with file_path.open(mode='r') as f:
                return json.load(f)


def check_file_existence(client, bucket: str, key: str) -> bool:
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        elif e.response['Error']['Code'] == 403:
            # Unauthorized, including invalid bucket
            raise e
        else:
            # Something else has gone wrong.
            raise e


def get_client(service_name):
    if "AWS_MOCK_URL" in os.environ and isinstance(os.environ["AWS_MOCK_URL"], str):
        client = boto3.client(service_name, endpoint_url=os.environ["AWS_MOCK_URL"])
    else:
        client = boto3.client(service_name)
    return client


def load_gzip_file_from_s3(client, bucket: str, key: str, file_path: Path) -> JSON:
    s3_client = client
    file_is_found = download_s3_file(client=s3_client, bucket=bucket, key=key, absolute_path=str(file_path))
    if file_is_found:
        with gzip.open(str(file_path), 'rb') as f:
            file_content = json.loads(f.read().decode())
        file_path.unlink()
        return file_content
    else:
        raise ValueError(f"file not found at {bucket}/{key}")


def save_json_to_s3_in_gzip_format(client, bucket: str, key: str, json_content: JSON) -> None:
    s_in = json.dumps(json_content).encode()
    s_out = gzip.compress(s_in)
    client.put_object(Body=s_out, Bucket=bucket, Key=key)
