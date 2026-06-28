output "droplet_ip" {
  description = "The Droplets public IPv4 address"
  value       = try(digitalocean_droplet.app.ipv4_address, null)
}