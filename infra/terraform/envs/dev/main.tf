terraform {
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = "us-east-1"
}

module "ml_serving" {
  source        = "../../modules/ml-serving"
  environment   = "dev"
  service_name  = "mlops-inference"
  model_version = "0.1.0"
}
