variable "aws_region" {
  description = "AWS Region selected by the project owner."
  type        = string
}

variable "aws_profile" {
  description = "Optional AWS CLI profile; null uses the default credential chain."
  type        = string
  default     = null
}

variable "project_name" {
  description = "Prefix for Day 1 resource names."
  type        = string
  default     = "intelligent-cms"
}

variable "environment" {
  description = "Short environment label."
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "Tags applied to supported resources."
  type        = map(string)
  default = {
    Project     = "aws-intelligent-content-platform"
    Environment = "dev"
  }
}
