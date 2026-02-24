# iac-aws

Infrastructure as Code (IaC) for AWS using Ansible - A modular, declarative approach to managing AWS cloud resources.

## Overview

This repository provides Ansible-based automation for provisioning and managing AWS infrastructure in a repeatable, idempotent manner. It separates infrastructure definitions (configuration files) from automation logic (playbooks), making it easy to version control your infrastructure and apply changes safely.

## Features

- **Modular Design**: Separate playbooks for VPC, IAM, EC2, and S3 resources
- **Declarative Configuration**: Define your infrastructure in YAML configuration files
- **Idempotent Operations**: Safe to run multiple times without side effects
- **Custom Filters**: Built-in Jinja2 filters for AWS resource name-to-ID resolution
- **Safe Teardown**: Confirmation-required teardown playbook for resource cleanup

## AWS Resources Managed

### VPC Stack
- VPCs and Subnets
- Internet Gateways and NAT Gateways
- Route Tables and Network ACLs
- Security Groups
- VPC Endpoints (Gateway and Interface types)

### Compute
- EC2 Instances with IAM role attachment

### Identity & Access Management
- IAM Users, Roles, and Instance Profiles
- Role policies and managed policies

### Storage
- S3 Buckets

## Prerequisites

- **Python 3.6+** (tested with Ansible 2.16.14 which supports Python 3.6)
- **AWS Credentials** configured (via AWS CLI, environment variables, or IAM roles)
- **Ansible** and required collections (see [Setup](#setup))

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r automation/setup/requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r automation/setup/requirements.yml
```

### 2. Configure AWS Credentials

Ensure your AWS credentials are configured:

```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Define Your Infrastructure

Edit configuration files in the `configs/` directory to define your desired infrastructure (see [Configuration](#configuration) for details).

### 4. Run Playbooks

```bash
cd automation

# Create VPC infrastructure
ansible-playbook iac-vpc.yml

# Create IAM resources
ansible-playbook iac-iam.yml

# Create EC2 instances
ansible-playbook iac-ec2.yml

# Create S3 buckets
ansible-playbook iac-s3.yml

# Or run all at once
ansible-playbook iac-vpc.yml iac-iam.yml iac-ec2.yml iac-s3.yml
```

## Repository Structure

```
iac-aws/
├── automation/              # Ansible playbooks and automation logic
│   ├── ansible.cfg         # Ansible configuration
│   ├── iac-vpc.yml         # VPC infrastructure playbook
│   ├── iac-iam.yml         # IAM resources playbook
│   ├── iac-ec2.yml         # EC2 instances playbook
│   ├── iac-s3.yml          # S3 buckets playbook
│   ├── iac-teardown.yml    # Resource teardown playbook
│   ├── group_vars/         # Global variables
│   │   └── all.yml         # Configuration directory path
│   ├── tasks/              # Reusable task files
│   │   └── copy_configs.yml # Config file loader
│   ├── plugins/            # Custom Ansible plugins
│   │   └── filter/         # Custom Jinja2 filters
│   │       └── aws_filters.py # AWS resource resolution filters
│   └── setup/              # Setup and requirements
│       ├── requirements.txt     # Python dependencies
│       └── requirements.yml     # Ansible collections
└── configs/                # Infrastructure definitions (YAML)
    ├── vpc.yml             # VPC definitions
    ├── vpc-subnets.yml     # Subnet definitions
    ├── vpc-internet-gateways.yml
    ├── vpc-nat-gateways.yml
    ├── vpc-route-tables.yml
    ├── vpc-network-acls.yml
    ├── vpc-security-groups.yml
    ├── vpc-endpoints.yml
    ├── ec2-instances.yml   # EC2 instance definitions
    ├── iam-users.yml       # IAM user definitions
    ├── iam-roles.yml       # IAM role definitions
    ├── iam-instance-profiles.yml
    └── s3-buckets.yml      # S3 bucket definitions
```

## Configuration

Infrastructure is defined in YAML files located in the `configs/` directory. Each file contains a dictionary of resource definitions.

### Example: VPC Configuration (`configs/vpc.yml`)

```yaml
scas-vpc-a:
  - name: scas-vpc-a
    region: us-east-1
    cidr_block: 10.0.0.0/16

scas-vpc-b:
  - name: scas-vpc-b
    region: us-east-1
    cidr_block: 10.1.0.0/16
```

### Configuration File Reference

| File | Purpose | Key Fields |
|------|---------|------------|
| `vpc.yml` | VPC definitions | name, region, cidr_block |
| `vpc-subnets.yml` | Subnet definitions | name, vpc_name, cidr_block, az, type |
| `vpc-internet-gateways.yml` | Internet gateway definitions | vpc_name, region, tags |
| `vpc-nat-gateways.yml` | NAT gateway definitions | subnet_name, region, tags |
| `vpc-route-tables.yml` | Route table definitions | name, vpc_name, subnets, routes |
| `vpc-network-acls.yml` | Network ACL definitions | name, vpc_name, subnets, rules |
| `vpc-security-groups.yml` | Security group definitions | name, vpc_name, description, rules |
| `vpc-endpoints.yml` | VPC endpoint definitions | service, vpc_name, type, subnets |
| `ec2-instances.yml` | EC2 instance definitions | name, instance_type, image_id, subnet, security_groups |
| `iam-users.yml` | IAM user definitions | name, policies |
| `iam-roles.yml` | IAM role definitions | name, assume_role_policy, policies |
| `iam-instance-profiles.yml` | IAM instance profile definitions | name, role_name |
| `s3-buckets.yml` | S3 bucket definitions | name, region, versioning, encryption |

## Usage

### Running Specific Resource Types

Use Ansible tags to run specific parts of the VPC playbook:

```bash
# Create only VPCs
ansible-playbook iac-vpc.yml --tags vpc

# Create only subnets
ansible-playbook iac-vpc.yml --tags vpc-subnets

# Create security groups only
ansible-playbook iac-vpc.yml --tags vpc-security-groups
```

Available tags:
- `vpc` - VPCs, Internet Gateways, Subnets, NAT Gateways, Route Tables, NACLs, Security Groups, Endpoints
- `vpc-internet-gateways`
- `vpc-subnets`
- `vpc-nat-gateways`
- `vpc-route-tables`
- `vpc-network-acls`
- `vpc-security-groups`
- `vpc-endpoints`

### Custom Filters

The repository includes custom Jinja2 filters for resolving resource names to AWS IDs:

- `get_aws_resource_id(resource_type, region)` - Resolve a single resource name to its AWS ID
- `get_aws_resource_ids(resource_type, region)` - Resolve multiple resource names to AWS IDs
- `resolve_route_gateway_ids(route, region)` - Resolve gateway names in route definitions
- `get_nat_gateway_by_subnet(subnet_name, region)` - Get NAT gateway ID by subnet name

Example usage in playbooks:
```yaml
vpc_id: '{{ vpc_name | get_aws_resource_id("vpc", region) }}'
```

### Teardown

To destroy all managed resources:

```bash
cd automation

# DANGER: This will delete resources - requires confirmation
ansible-playbook iac-teardown.yml -e confirm_teardown=yes
```

**⚠️ WARNING**: The teardown playbook will delete resources in reverse dependency order. Always review what will be deleted before running this command.

## Troubleshooting

### Common Issues

**Issue**: Playbook fails with "resource not found" error
- **Solution**: Ensure dependent resources are created first (e.g., VPC before subnets)
- Run playbooks in order: VPC → IAM → EC2 → S3

**Issue**: AWS credentials not found
- **Solution**: Configure AWS credentials using `aws configure` or environment variables

**Issue**: Module not found errors
- **Solution**: Install Ansible collections: `ansible-galaxy collection install -r automation/setup/requirements.yml`

**Issue**: Python boto3 errors
- **Solution**: Install Python dependencies: `pip install -r automation/setup/requirements.txt`

### Debugging

Enable verbose output:
```bash
# Verbose mode
ansible-playbook iac-vpc.yml -v

# Very verbose (shows task execution)
ansible-playbook iac-vpc.yml -vv

# Debug mode (shows all details)
ansible-playbook iac-vpc.yml -vvv
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes in the appropriate config or playbook files
3. Test your changes in a non-production AWS account
4. Submit a pull request with a clear description of changes

## License

This project is provided as-is for educational and operational purposes.

## Support

For issues, questions, or contributions, please open an issue in the GitHub repository.
