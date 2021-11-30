terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.65"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-east-2"
}

resource "aws_instance" "video_stream_ec2" {
  # Will need to create an ami for use
  # ami           = ""
  instance_type = "t2.micro"

  tags = {
    Name = "VideoStreamInstance"
  }
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "jaywalker-final-s3"
  acl    = "private"
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "jaywalker-temp-s3"
  acl    = "private"
}

resource "aws_sns_topic" "sns_emails" {
  name = "sns-notif"
}

resource "aws_dynamodb_table" "basic-dynamodb-table" {
  name           = "GameScores"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "Image"
  range_key      = "Date"

  attribute {
    name = "Image"
    type = "S"
  }

  attribute {
    name = "Date"
    type = "S"
  }
}