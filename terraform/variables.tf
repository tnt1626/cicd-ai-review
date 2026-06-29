variable "do_token" {
  type        = string
  description = "Digitalocean API Token"
  sensitive   = true
}

variable "region" {
  type        = string
  default     = "sgp1"
  description = "Region of the VM"
}

variable "size" {
  type        = string
  default     = "s-1vcpu-1gb"
  description = "Droplet size"
}

variable "image" {
  type        = string
  default     = "ubuntu-22-04-x64"
  description = "Image of droplet"
}

variable "ssh_key_id" {
  type = string
}