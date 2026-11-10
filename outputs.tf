output "bucket_name" {
  value = aws_s3_bucket.seguro.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.seguro.arn
}

output "sse_algorithm" {
  value = one(aws_s3_bucket_server_side_encryption_configuration.seguro.rule[*].apply_server_side_encryption_by_default[0].sse_algorithm)
}
