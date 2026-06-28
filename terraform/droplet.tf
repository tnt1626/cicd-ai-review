resource "digitalocean_droplet" "app" {
  name     = "cicd-ai-review"
  region   = var.region
  size     = var.size
  image    = var.image
  ssh_keys = [var.ssh_key_id]
}