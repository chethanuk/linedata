variable "env" {
  description = "which environment"
  type        = string
  default     = "staging"
}

variable "region" {
  description = "region of your aws account profile"
  type        = string
  default     = "ap-southeast-1"
}

variable "profile" {
  description = "profile name of your aws credential"
  type        = string
  default     = "staging"
}

variable "prefix" {
  description = "prefix of a name, like data-labeling-platform"
  type        = string
  default     = "lldc"
}

locals {
  prefix_with_env = "${var.prefix}-${var.env}"
}