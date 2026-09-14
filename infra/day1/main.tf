terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.0, < 3.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

locals {
  name = "${var.project_name}-${var.environment}"
}

data "archive_file" "content_api" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/content-api.zip"
}

resource "aws_dynamodb_table" "content" {
  name         = "${local.name}-content"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  tags = var.tags
}

resource "aws_iam_role" "content_api" {
  name = "${local.name}-content-api"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "content_api" {
  name              = "/aws/lambda/${local.name}-content-api"
  retention_in_days = 7
  tags              = var.tags
}

resource "aws_iam_role_policy" "content_api" {
  name = "${local.name}-content-api"
  role = aws_iam_role.content_api.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem"]
        Resource = aws_dynamodb_table.content.arn
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem"]
        Resource = aws_dynamodb_table.content.arn
        Condition = {
          "ForAnyValue:StringEquals" = {
            "dynamodb:EnclosingOperation" = "TransactWriteItems"
          }
        }
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "${aws_cloudwatch_log_group.content_api.arn}:*"
      }
    ]
  })
}

resource "aws_lambda_function" "content_api" {
  function_name    = "${local.name}-content-api"
  filename         = data.archive_file.content_api.output_path
  source_code_hash = data.archive_file.content_api.output_base64sha256
  role             = aws_iam_role.content_api.arn
  handler          = "content_api.handler.lambda_handler"
  runtime          = "python3.12"
  memory_size      = 256
  timeout          = 10

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.content.name
    }
  }

  depends_on = [aws_iam_role_policy.content_api, aws_cloudwatch_log_group.content_api]
  tags       = var.tags
}

resource "aws_apigatewayv2_api" "management" {
  name          = "${local.name}-management"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "content_api" {
  api_id                 = aws_apigatewayv2_api.management.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.content_api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "create_content" {
  api_id             = aws_apigatewayv2_api.management.id
  route_key          = "POST /content"
  authorization_type = "AWS_IAM"
  target             = "integrations/${aws_apigatewayv2_integration.content_api.id}"
}

resource "aws_apigatewayv2_route" "get_content" {
  api_id             = aws_apigatewayv2_api.management.id
  route_key          = "GET /content/{id}"
  authorization_type = "AWS_IAM"
  target             = "integrations/${aws_apigatewayv2_integration.content_api.id}"
}

resource "aws_apigatewayv2_route" "update_content" {
  api_id             = aws_apigatewayv2_api.management.id
  route_key          = "PUT /content/{id}"
  authorization_type = "AWS_IAM"
  target             = "integrations/${aws_apigatewayv2_integration.content_api.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.management.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowManagementApi"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.content_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.management.execution_arn}/*/*"
}
