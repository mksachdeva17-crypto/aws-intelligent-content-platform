output "management_api_url" {
  description = "IAM-authenticated Day 1 demo API. Day 7 adds Cognito and content roles."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "content_table_name" {
  value = aws_dynamodb_table.content.name
}

output "content_api_function_name" {
  value = aws_lambda_function.content_api.function_name
}
