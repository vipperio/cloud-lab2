variable "aws_region" {
  type    = string
  default = "eu-north-1"
}
variable "project_name" {
  type    = string
  default = "cloud-lab2"
}
variable "min_capacity" {
  type    = number
  default = 1
}
variable "max_capacity" {
  type    = number
  default = 4
}
variable "cpu_target" {
  type    = number
  default = 60
}
variable "alert_email" {
  description = "Email to receive ALARM and OK notifications; empty disables the email subscription"
  type        = string
  default     = ""
}

variable "allowed_client_cidr" {
  description = "Trusted client public IPv4 CIDR"
  type        = string
}


