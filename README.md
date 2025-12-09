# AWS Infrastructure as Code (IAC)

This repository contains Terraform configurations for managing AWS infrastructure.

## Overview

This IAC project provides foundational AWS infrastructure components including:
- VPC (Virtual Private Cloud)
- Public and Private Subnets
- Internet Gateway
- Route Tables and Associations

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- AWS Account with appropriate credentials configured
- AWS CLI (optional, for credential management)

## Project Structure

```
.
├── main.tf                      # Main infrastructure resources
├── provider.tf                  # AWS provider configuration
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
├── versions.tf                  # Terraform and provider version constraints
├── terraform.tfvars.example     # Example variable values
└── README.md                    # This file
```

## Getting Started

### 1. Configure AWS Credentials

Ensure your AWS credentials are configured. You can use one of the following methods:

**Option A: AWS CLI Configuration**
```bash
aws configure
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 2. Configure Variables

Copy the example variables file and customize it for your environment:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` to set your desired values:
- `aws_region`: AWS region for resources
- `project_name`: Name of your project
- `environment`: Environment name (dev, staging, prod)
- `vpc_cidr`: CIDR block for your VPC
- `availability_zones`: List of AZs to use
- `public_subnet_cidrs`: CIDR blocks for public subnets
- `private_subnet_cidrs`: CIDR blocks for private subnets

### 3. Initialize Terraform

Initialize the Terraform working directory:

```bash
terraform init
```

### 4. Plan Infrastructure Changes

Review the planned infrastructure changes:

```bash
terraform plan
```

### 5. Apply Infrastructure

Create the infrastructure:

```bash
terraform apply
```

Type `yes` when prompted to confirm the changes.

### 6. View Outputs

After applying, view the infrastructure outputs:

```bash
terraform output
```

## Resources Created

- **VPC**: A Virtual Private Cloud with DNS support enabled
- **Internet Gateway**: Provides internet access to the VPC
- **Public Subnets**: Subnets with internet access (2 by default, one per AZ)
- **Private Subnets**: Isolated subnets without direct internet access (2 by default)
- **Route Tables**: Separate route tables for public and private subnets
- **Route Table Associations**: Links subnets to their respective route tables

## Outputs

The following outputs are available after applying:

- `vpc_id`: The ID of the created VPC
- `vpc_cidr`: The CIDR block of the VPC
- `public_subnet_ids`: List of public subnet IDs
- `private_subnet_ids`: List of private subnet IDs
- `internet_gateway_id`: The ID of the Internet Gateway
- `public_route_table_id`: ID of the public route table
- `private_route_table_id`: ID of the private route table

## Destroying Infrastructure

To destroy all resources created by this configuration:

```bash
terraform destroy
```

Type `yes` when prompted to confirm.

## Security Considerations

- All resources are tagged with `ManagedBy = "Terraform"` for easy identification
- Private subnets do not have direct internet access
- The `.gitignore` file prevents committing sensitive files like `.tfvars` and state files
- Always use appropriate IAM permissions and follow the principle of least privilege

## Customization

You can customize the infrastructure by modifying the variables in `terraform.tfvars` or by passing variables via command line:

```bash
terraform apply -var="environment=prod" -var="vpc_cidr=10.1.0.0/16"
```

## Contributing

When making changes:
1. Test your changes in a separate environment
2. Update documentation as needed
3. Follow Terraform best practices

## License

This project is provided as-is for infrastructure management purposes.
