terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_vpc" "default_vpc" {
  default = true
}

resource "aws_key_pair" "sunil" {
  key_name   = "sunil"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_security_group" "backend_sg" {
  name        = "backend-sg"
  description = "Allow SSH, HTTP, and HTTPS"
  vpc_id      = data.aws_vpc.default_vpc.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "App"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "backend-sg"
  }
}

resource "aws_instance" "backend_instance" {
  ami           = "ami-0360c520857e3138f"
  instance_type = "t2.micro"
  key_name      = aws_key_pair.sunil.key_name

  vpc_security_group_ids = [aws_security_group.backend_sg.id]

  tags = {
    Name = "backend-instance"
  }

  user_data = <<-EOF
    #!/bib/bash
    echo "Hello world 2" > index.html
    python3 -m http.server 8080 & 
    EOF
}

// instance 2
resource "aws_instance" "backend_instance_2" {
  ami           = "ami-0360c520857e3138f"
  instance_type = "t2.micro"
  key_name      = aws_key_pair.sunil.key_name

  vpc_security_group_ids = [aws_security_group.backend_sg.id]

  tags = {
    Name = "backend-instance"
  }

  user_data = <<-EOF
    #!/bib/bash
    echo "Hello world 2" > index.html
    python3 -m http.server 8080 & 
    EOF
}

// Load Balancer

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb_target_group.instances.arn

  port     = 80
  protocol = "HTTP"

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "404: page not found"
      status_code  = 404
    }
  }
}

resource "aws_lb_target_group" "instances" {
  name     = "decoder-target-group"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default_vpc.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

// S3-Bucket
resource "aws_s3_bucket" "bucket" {
  bucket        = "video-decoder-v20"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
