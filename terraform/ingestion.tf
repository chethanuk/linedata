#module "ingestion-stream" {
#  source      = "./modules/kinesis-firehose-s3-stream"
#  module-name = "${local.prefix_with_env}-ingestion-stream"
#}
#
#resource "aws_ssm_parameter" "ingestion-kinesis" {
#  name        = replace("${local.prefix_with_env}-kinesis-stream", "-", "_")
#  description = "kinesis-stream-name"
#  type        = "SecureString"
#  value       = module.ingestion-stream.kinesis-stream-name
#}
#
#output "kinesis-stream-name" {
#  value = aws_ssm_parameter.ingestion-kinesis.name
#}

resource "aws_s3_bucket" "ingestion-bucket1" {
  bucket_prefix = "${local.prefix_with_env}-ingestion-bucket1"
}

resource "aws_s3_bucket_acl" "bucket-acl" {
  bucket = aws_s3_bucket.ingestion-bucket1.id
  acl    = "private"
}

resource "aws_ssm_parameter" "ingestion-bucket1" {
  name        = replace("${local.prefix_with_env}-ingestion-bucket1", "-", "_")
  description = "ingestion-bucket1"
  type        = "SecureString"
  value       = aws_s3_bucket.ingestion-bucket1.id
}

output "ingestion-bucket1" {
  value = aws_ssm_parameter.ingestion-bucket1.name
}

resource aws_s3_bucket_notification "ingestion-bucket1" {
  bucket      = aws_s3_bucket.ingestion-bucket1.id
  eventbridge = true
}