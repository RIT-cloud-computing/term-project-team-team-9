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
