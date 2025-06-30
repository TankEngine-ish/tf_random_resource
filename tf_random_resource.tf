terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

resource "random_string" "example" {
  length  = 16
  special = false
}

output "result" {
  value = random_string.example.result
}