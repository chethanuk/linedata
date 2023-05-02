import os
from dataclasses import dataclass
from pathlib import Path

import line_level_data_collection.s3_helper as s3_helper
from line_level_data_collection.data_update_event import DataEntryUpdateEvent
from line_level_data_collection.time_util import utc_datetime_now


@dataclass
class S3ObjectCreatedEvent:
    bucket: str
    key: str


class EventAggregator:
    # /tmp path can hold up to 10 G data
    # https://aws.amazon.com/blogs/aws/aws-lambda-now-supports-up-to-10-gb-ephemeral-storage/
    def __init__(
            self,
            s3_client,
            aggregation_bucket: str,
            max_count: int,
            tmp_dir: Path = Path('/tmp'),
    ):
        # you'll need list bucket and get bucket permission
        self.s3_client = s3_client
        self.aggregation_bucket = aggregation_bucket
        self.tmp_dir = tmp_dir
        self.max_count = max_count

    def load_latest_from_s3(self, bucket: str, key: str):
        # need listbucket and getobject permission
        file_exists = s3_helper.check_file_existence(client=self.s3_client, bucket=self.aggregation_bucket, key=key)
        if file_exists:
            file_path = self.tmp_dir / "random.json.gzip"
            bucket = self.aggregation_bucket
            return s3_helper.load_gzip_file_from_s3(client=self.s3_client, key=key, file_path=file_path, bucket=bucket)
        else:
            return []

    def _save_file_to_s3_in_gzip(self, json_content: s3_helper.JSON, bucket: str, key: str):
        s3_helper.save_json_to_s3_in_gzip_format(client=self.s3_client, bucket=bucket, key=key,
                                                 json_content=json_content)

    def _remove_s3_object(self, bucket: str, key: str):
        self.s3_client.delete_object(Bucket=bucket, Key=key)

    def process_event(self, event: S3ObjectCreatedEvent):
        # get object
        event_json = s3_helper.download_s3_file_and_load_content(client=self.s3_client, bucket=event.bucket,
                                                                 key=event.key)
        # validate object
        # TODO: this can be parametrized
        update_event: DataEntryUpdateEvent = DataEntryUpdateEvent.from_dict(event_json)
        language = update_event.language

        # get latest from s3
        key = f"{language}/latest.json.gzip"
        aggregated = self.load_latest_from_s3(bucket=self.aggregation_bucket, key=key)

        # update accumulated content
        aggregated.append(update_event.to_dict())

        # write back the result
        should_finish_aggregation = len(aggregated) >= self.max_count
        if should_finish_aggregation:
            # if enough, write to new entry
            # remove previous s3 object
            timestamp_in_seconds = int(round(utc_datetime_now().timestamp()))
            new_key = f"{language}/{timestamp_in_seconds}.json.gzip"
            self._save_file_to_s3_in_gzip(json_content=aggregated, bucket=self.aggregation_bucket, key=new_key)
            # note: this will not remove the objects if the bucket has versioning enabled
            # https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html
            self._remove_s3_object(bucket=self.aggregation_bucket, key=key)
        else:
            self._save_file_to_s3_in_gzip(json_content=aggregated, bucket=self.aggregation_bucket, key=key)

        # removed processed object
        self._remove_s3_object(bucket=event.bucket, key=event.key)


def aggregate_events(event, context):
    event = S3ObjectCreatedEvent(bucket=event['detail']['bucket']['name'], key=event['detail']['object']['key'])
    target_bucket = os.environ['S3_BUCKET']
    capacity = int(os.environ['CAPACITY'])
    client = s3_helper.get_client('s3')
    aggregator = EventAggregator(
        s3_client=client,
        aggregation_bucket=target_bucket,
        max_count=capacity
    )
    aggregator.process_event(event=event)
