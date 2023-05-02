terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # Allows only the rightmost version component to increment
      version = "~> 4.16"
    }
#    archive = {
#      source  = "hashicorp/archive"
#      version = "~> 2.2.0"
#    }
#    git = {
#      source  = "innovationnorway/git"
#      version = "0.1.3"
#    }
    random = {
      source  = "hashicorp/random"
      version = "3.1.0"
    }
  }

  required_version = ">= 1.2.0"

  # A backend block cannot refer to named values (like input variables, locals, or data source attributes).
  # better to manually creat it. instead of by terraform.
  # original staging account
#  backend "s3" {
#    bucket  = "line-level-data-collection-tf-state"
#    key     = "terraform.tfstate"
#    profile = "staging"
#    region  = "ap-southeast-1"
#
#    skip_metadata_api_check     = true
#    skip_region_validation      = true
#    skip_credentials_validation = true
#  }

  backend "s3" {
    bucket  = "line-level-data-collection-tf-state-0001"
    key     = "terraform.tfstate"
    profile = "staging"
    region  = "ap-southeast-1"

    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_credentials_validation = true
  }

}

provider "aws" {
  profile = var.profile
  region  = var.region

  default_tags {
    tags = {
      Environment = var.env
      Service     = "LineLevelDataCollection"
    }
  }
  # Make it faster by skipping something
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

data "aws_caller_identity" "current" {}

provider "random" {
  # Configuration options
}
