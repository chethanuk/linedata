#### Firehose configuration
resource "aws_kinesis_firehose_delivery_stream" "extended_s3_stream" {
  name        = "${var.module-name}-firehose-stream"
  destination = "extended_s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.test_stream.arn
    role_arn           = aws_iam_role.firehose_role.arn
  }

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn

    # Example prefix using partitionKeyFromQuery, applicable to JQ processor
    #    prefix              = "data/customer_id=!{partitionKeyFromQuery:customer_id}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"
    #    error_output_prefix = "errors/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/!{firehose:error-output-type}/"

    # https://docs.aws.amazon.com/firehose/latest/dev/dynamic-partitioning.html
    # TODO: use a different config for production environment
    buffer_size     = 2
    buffer_interval = 60

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.ingestion-log-group.name
      log_stream_name = aws_cloudwatch_log_stream.ingestion-log-stream.name
    }
    #    processing_configuration {
    #      enabled = "true"
    #
    #      # Multi-record deaggregation processor example
    #      processors {
    #        type = "RecordDeAggregation"
    #        parameters {
    #          parameter_name  = "SubRecordType"
    #          parameter_value = "JSON"
    #        }
    #      }
    #
    #      # New line delimiter processor example
    #      processors {
    #        type = "AppendDelimiterToRecord"
    #      }
    #
    #      # JQ processor example
    #      processors {
    #        type = "MetadataExtraction"
    #        parameters {
    #          parameter_name  = "JsonParsingEngine"
    #          parameter_value = "JQ-1.6"
    #        }
    #        parameters {
    #          parameter_name  = "MetadataExtractionQuery"
    #          parameter_value = "{customer_id:.customer_id}"
    #        }
    #      }
    #    }
  }
}

### s3 config
resource "aws_s3_bucket" "bucket" {
  bucket_prefix = "${var.module-name}-fb"
}

resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.bucket.id
  acl    = "private"
}

### firehose role config
resource "aws_iam_role" "firehose_role" {
  name = "firehose_test_role"

  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "firehose.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  }
  EOF
}

### firehose role config - can write to s3
resource "aws_iam_role_policy_attachment" "firehose-ingestion-s3-policy" {
  role       = aws_iam_role.firehose_role.name
  policy_arn = aws_iam_policy.ingestion.arn
}

resource "aws_iam_policy" "ingestion" {
  name        = "${var.module-name}-ingestion-module-s3-policy"
  description = "ingestion module policy"
  policy      = jsonencode(
    {
      Statement = [
        {
          Action = [
            "s3:AbortMultipartUpload",
            "s3:GetBucketLocation",
            "s3:GetObject",
            "s3:ListBucket",
            "s3:ListBucketMultipartUploads",
            "s3:PutObject",
          ]
          Effect   = "Allow"
          Resource = [
            "${aws_s3_bucket.bucket.arn}",
            "${aws_s3_bucket.bucket.arn}/*"
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )
}


#### Cloud watch configuration
resource "aws_cloudwatch_log_group" "ingestion-log-group" {
  name_prefix = "${var.module-name}-ingestion-log-group"
}

### firehose role config - can write to cloud watch
resource "aws_cloudwatch_log_stream" "ingestion-log-stream" {
  name           = "ingestion-log-stream"
  log_group_name = aws_cloudwatch_log_group.ingestion-log-group.name
}

######### Kinesis data stream config
resource "aws_kinesis_stream" "test_stream" {
  name             = "${var.module-name}-kinese-stream"
  retention_period = 48
  stream_mode_details {
    stream_mode = "ON_DEMAND"
  }
}

### firehose role config - can read the kinesis data stream
resource "aws_iam_role_policy_attachment" "ingestion-kinesis" {
  role       = aws_iam_role.firehose_role.name
  policy_arn = aws_iam_policy.ingestion-kinesis-consumption.arn
}

resource "aws_iam_policy" "ingestion-kinesis-consumption" {
  name        = "${var.module-name}-ingestion-module-read-kinesis"
  description = "ingestion module policy"
  policy      = jsonencode(
    {
      Statement = [
        {
          Action : [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          Resource : "*",
          Effect : "Allow"
        },
        {
          Action : [
            "kinesis:*"
          ],
          Resource : [
            aws_kinesis_stream.test_stream.arn
          ],
          Effect : "Allow"
        }
      ]
      Version = "2012-10-17"
    }
  )
}