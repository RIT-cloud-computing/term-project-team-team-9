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

  bucket = "jaywalker-s3-bucket"
  acl    = "private"
}

resource "aws_sns_topic" "sns_emails" {
  name = "sns-notif"
}

module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 3.0"

  identifier = "offending-db"

  engine            = "mysql"
  engine_version    = "8.0.23"
  instance_class    = "db.t2.micro"
  allocated_storage = 20

  name     = "offending-db"
  username = "admin"
  password = "YourPwdShouldBeLongAndSecure!"
  port     = "3306"

  # DB subnet group
  subnet_ids = []

  # Database Deletion Protection
  deletion_protection = true

}