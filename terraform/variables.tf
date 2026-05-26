# Stage 4 LIVE variables (Batch 373 C-2 SKELETON)

variable "activated" {
  description = "Master flag - false (default) = SKELETON, no resources created. Set true ONLY when owner triggers Stage 4 activation."
  type        = bool
  default     = false
}

variable "aws_region" {
  description = "AWS region for Lightsail instance"
  type        = string
  default     = "us-east-1"  # NYSE/NASDAQ data centers
}

variable "instance_bundle" {
  description = "Lightsail bundle (nano_2_0 = $5/mo / 1 vCPU / 2 GB / 60 GB SSD)"
  type        = string
  default     = "nano_2_0"
}

variable "ssh_key_name" {
  description = "Lightsail SSH key pair name (owner-created via Lightsail console)"
  type        = string
  default     = "stock-picks-owner-key"
}

variable "ssh_cidrs" {
  description = "Allowed SSH source IPs - restrict to owner home/office only"
  type        = list(string)
  default     = []  # MUST be set by owner; empty = no SSH access
}

variable "repo_url" {
  description = "Git repo URL for instance bootstrap"
  type        = string
  default     = "https://github.com/jeetmehta1991/stock-picks-app.git"
}
