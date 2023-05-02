output "kinesis-stream-name" {
  value = aws_kinesis_stream.test_stream.name
}

output "firehose-output-bucket-arn" {
  value = aws_s3_bucket.bucket.arn
}