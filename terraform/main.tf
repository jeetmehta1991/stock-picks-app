# Stage 4 LIVE infrastructure - AWS Lightsail (Batch 373 C-2 SKELETON)
#
# Status: SKELETON ONLY. Values are placeholders; activation requires owner-
# supplied AWS account + credentials per terraform/README.md.
#
# Owner activation sequence:
#   1. terraform init
#   2. terraform plan -var="aws_region=us-east-1" -var="ssh_key_name=<owner-key>"
#   3. terraform apply (after review)
#
# Expected cost: $5-12/mo (nano instance + EBS snapshot retention).

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Backend: local for skeleton; owner switches to S3 + DynamoDB lock on activation
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region
}

# Daily-picks instance (Stage 4 cron host)
resource "aws_lightsail_instance" "picks_runner" {
  count             = var.activated ? 1 : 0
  name              = "stock-picks-runner"
  availability_zone = "${var.aws_region}a"
  blueprint_id      = "ubuntu_22_04"
  bundle_id         = var.instance_bundle
  key_pair_name     = var.ssh_key_name

  # Bootstrap script - pulls main + installs deps + sets cron
  user_data = templatefile("${path.module}/bootstrap.sh.tpl", {
    repo_url = var.repo_url
    region   = var.aws_region
  })

  tags = {
    Project = "stock-picks"
    Stage   = "4-live-trading"
    Owner   = "jeetmehta1991"
  }
}

# EBS snapshot policy - 7-day retention DR
resource "aws_lightsail_instance_public_ports" "picks_runner_ports" {
  count          = var.activated ? 1 : 0
  instance_name  = aws_lightsail_instance.picks_runner[0].name
  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
    cidrs     = var.ssh_cidrs  # restrict to owner IPs only
  }
  # NO inbound 80/443 - this is a cron host, not a web server
}

# SSM Parameter Store for Anthropic + IB credentials
# Owner runs `aws ssm put-parameter` post-apply; do NOT commit values here.
resource "aws_ssm_parameter" "anthropic_api_key_placeholder" {
  count       = var.activated ? 1 : 0
  name        = "/stock-picks/anthropic_api_key"
  type        = "SecureString"
  description = "Anthropic Console API key (Stage 4 LIVE agent calls)"
  value       = "PLACEHOLDER_RUN_AWS_SSM_PUT_PARAMETER_POST_APPLY"
  lifecycle {
    ignore_changes = [value]
  }
  tags = {
    Project = "stock-picks"
    Owner   = "jeetmehta1991"
  }
}

resource "aws_ssm_parameter" "ib_account_placeholder" {
  count       = var.activated ? 1 : 0
  name        = "/stock-picks/ib_account"
  type        = "SecureString"
  description = "Interactive Brokers account credentials"
  value       = "PLACEHOLDER_RUN_AWS_SSM_PUT_PARAMETER_POST_APPLY"
  lifecycle {
    ignore_changes = [value]
  }
}

output "instance_public_ip" {
  value       = var.activated ? aws_lightsail_instance.picks_runner[0].public_ip_address : null
  description = "SSH target (when activated)"
}

output "activation_status" {
  value       = var.activated ? "ACTIVATED" : "SKELETON-ONLY (Batch 373 C-2 default)"
  description = "Whether owner has triggered activation"
}
