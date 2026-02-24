# Quick Reference

This is a quick reference guide for common tasks and commands.

## Common Commands

### Setup

```bash
# Clone repository
git clone https://github.com/soterocasiano/iac-aws.git
cd iac-aws

# Install dependencies
pip install -r automation/setup/requirements.txt
ansible-galaxy collection install -r automation/setup/requirements.yml

# Configure AWS credentials
aws configure
```

### Deploy Infrastructure

```bash
cd automation

# Deploy everything
ansible-playbook iac-vpc.yml iac-iam.yml iac-ec2.yml iac-s3.yml

# Deploy specific resource types
ansible-playbook iac-vpc.yml              # VPC infrastructure only
ansible-playbook iac-iam.yml              # IAM resources only
ansible-playbook iac-ec2.yml              # EC2 instances only
ansible-playbook iac-s3.yml               # S3 buckets only

# Deploy specific VPC components using tags
ansible-playbook iac-vpc.yml --tags vpc                  # VPCs only
ansible-playbook iac-vpc.yml --tags vpc-subnets          # Subnets only
ansible-playbook iac-vpc.yml --tags vpc-security-groups  # Security groups only
```

### Validation and Testing

```bash
# Check syntax
ansible-playbook iac-vpc.yml --syntax-check

# Dry run (check mode)
ansible-playbook iac-vpc.yml --check

# Show what would change
ansible-playbook iac-vpc.yml --check --diff

# Verbose output
ansible-playbook iac-vpc.yml -v         # Basic verbosity
ansible-playbook iac-vpc.yml -vv        # More details
ansible-playbook iac-vpc.yml -vvv       # Even more details
```

### Teardown

```bash
cd automation

# Destroy all resources (requires confirmation)
ansible-playbook iac-teardown.yml -e confirm_teardown=yes
```

## AWS CLI Commands

### VPC Resources

```bash
# List VPCs
aws ec2 describe-vpcs --output table

# List VPCs with specific tag
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=my-vpc" --output table

# List subnets in a VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-12345678" --output table

# List security groups
aws ec2 describe-security-groups --output table

# List NAT gateways
aws ec2 describe-nat-gateways --output table

# List internet gateways
aws ec2 describe-internet-gateways --output table

# List route tables
aws ec2 describe-route-tables --output table
```

### EC2 Instances

```bash
# List all instances
aws ec2 describe-instances --output table

# List running instances
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --output table

# Get instance details
aws ec2 describe-instances --instance-ids i-12345678 --output json

# Get instance public IP
aws ec2 describe-instances --instance-ids i-12345678 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

### IAM Resources

```bash
# List IAM users
aws iam list-users --output table

# List IAM roles
aws iam list-roles --output table

# List instance profiles
aws iam list-instance-profiles --output table

# Get role details
aws iam get-role --role-name my-role --output json
```

### S3 Buckets

```bash
# List all buckets
aws s3 ls

# List bucket contents
aws s3 ls s3://my-bucket/

# Get bucket details
aws s3api get-bucket-versioning --bucket my-bucket
aws s3api get-bucket-encryption --bucket my-bucket
```

## Configuration File Locations

```
configs/
├── vpc.yml                      # VPC definitions
├── vpc-subnets.yml              # Subnet definitions
├── vpc-internet-gateways.yml    # Internet gateway definitions
├── vpc-nat-gateways.yml         # NAT gateway definitions
├── vpc-route-tables.yml         # Route table definitions
├── vpc-network-acls.yml         # Network ACL definitions
├── vpc-security-groups.yml      # Security group definitions
├── vpc-endpoints.yml            # VPC endpoint definitions
├── ec2-instances.yml            # EC2 instance definitions
├── iam-users.yml                # IAM user definitions
├── iam-roles.yml                # IAM role definitions
├── iam-instance-profiles.yml    # IAM instance profile definitions
└── s3-buckets.yml               # S3 bucket definitions
```

## Common Configuration Patterns

### Minimal VPC Configuration

```yaml
# configs/vpc.yml
my-vpc:
  - name: my-vpc
    region: us-east-1
    cidr_block: 10.0.0.0/16
```

### Public Subnet

```yaml
# configs/vpc-subnets.yml
my-subnet:
  - name: my-public-subnet
    vpc_name: my-vpc
    cidr_block: 10.0.1.0/24
    az: us-east-1a
    region: us-east-1
    map_public: true
    tags:
      Name: my-public-subnet
      Type: public
```

### Private Subnet

```yaml
# configs/vpc-subnets.yml
my-subnet:
  - name: my-private-subnet
    vpc_name: my-vpc
    cidr_block: 10.0.10.0/24
    az: us-east-1a
    region: us-east-1
    map_public: false
    tags:
      Name: my-private-subnet
      Type: private
```

### Basic Security Group

```yaml
# configs/vpc-security-groups.yml
my-sg:
  - name: my-web-sg
    vpc_name: my-vpc
    region: us-east-1
    description: "Web server security group"
    rules:
      - proto: tcp
        from_port: 80
        to_port: 80
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTP"
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTPS"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
    tags:
      Name: my-web-sg
```

### EC2 Instance

```yaml
# configs/ec2-instances.yml
my-instances:
  - name: my-web-server
    instance_type: t3.micro
    image_id: ami-0c55b159cbfafe1f0
    region: us-east-1
    vpc_subnet_id: my-public-subnet
    security_groups:
      - my-web-sg
    key_name: my-keypair
    tags:
      Name: my-web-server
```

### IAM Role for EC2

```yaml
# configs/iam-roles.yml
my-roles:
  - name: ec2-s3-role
    assume_role_policy_document:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Service: ec2.amazonaws.com
          Action: sts:AssumeRole
    managed_policies:
      - arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
    tags:
      Purpose: EC2 S3 access

# configs/iam-instance-profiles.yml
my-profiles:
  - name: ec2-s3-profile
    role_name: ec2-s3-role
```

## Troubleshooting Quick Reference

### Check Ansible Version

```bash
ansible-playbook --version
```

### Check Python and Boto3

```bash
python --version
python -c "import boto3; print(boto3.__version__)"
```

### Verify AWS Credentials

```bash
aws sts get-caller-identity
```

### List Ansible Collections

```bash
ansible-galaxy collection list | grep amazon
```

### Debug Playbook Execution

```bash
# Show all variables
ansible-playbook iac-vpc.yml -e debug=true

# Step through tasks
ansible-playbook iac-vpc.yml --step

# Start at specific task
ansible-playbook iac-vpc.yml --start-at-task="Create a VPC"
```

### Common Error Solutions

| Error | Solution |
|-------|----------|
| "Unable to locate credentials" | Run `aws configure` or set AWS environment variables |
| "module amazon.aws.* not found" | Run `ansible-galaxy collection install -r automation/setup/requirements.yml` |
| "No module named 'boto3'" | Run `pip install -r automation/setup/requirements.txt` |
| "VPC not found" | Ensure VPC is created before dependent resources |
| "DependencyViolation" | Run playbooks in order: VPC → IAM → EC2 → S3 |

## Resource Dependencies

Must be created in this order:

1. **VPC** → 2. **Internet Gateway** → 3. **Subnets** → 4. **NAT Gateway** → 5. **Route Tables** → 6. **Security Groups** → 7. **EC2 Instances**

Parallel with VPC:
- **IAM Roles** → **IAM Instance Profiles**
- **S3 Buckets** (no dependencies)

## Tags and Filters

### Ansible Tags

```bash
# VPC-related tags
--tags vpc                      # All VPC resources
--tags vpc-subnets              # Subnets only
--tags vpc-internet-gateways    # Internet gateways only
--tags vpc-nat-gateways         # NAT gateways only
--tags vpc-route-tables         # Route tables only
--tags vpc-network-acls         # Network ACLs only
--tags vpc-security-groups      # Security groups only
--tags vpc-endpoints            # VPC endpoints only
```

### AWS Resource Filters

```bash
# Filter by tag
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=my-vpc"

# Filter by state
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"

# Filter by VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-12345678"

# Combine filters
aws ec2 describe-instances --filters "Name=tag:Environment,Values=production" "Name=instance-state-name,Values=running"
```

## Environment Variables

### AWS Credentials

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Ansible Configuration

```bash
export ANSIBLE_CONFIG=/path/to/ansible.cfg
export ANSIBLE_INVENTORY=/path/to/inventory
```

## Useful One-Liners

```bash
# Count VPCs
aws ec2 describe-vpcs --query 'length(Vpcs)'

# Get all VPC IDs
aws ec2 describe-vpcs --query 'Vpcs[*].VpcId' --output text

# Get instance IPs
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,PrivateIpAddress]' --output table

# Find resources by tag
aws resourcegroupstaggingapi get-resources --tag-filters "Key=Environment,Values=production"

# Check AWS service health
aws health describe-events --filter eventTypeCategories=issue --query 'events[*].[eventTypeCode,startTime,endTime]' --output table
```

## Directory Quick Reference

```
iac-aws/
├── automation/              # Automation files (run playbooks from here)
│   ├── iac-*.yml           # Main playbooks
│   ├── ansible.cfg         # Ansible configuration
│   ├── group_vars/         # Variables
│   ├── plugins/filter/     # Custom filters
│   ├── setup/              # Dependencies
│   └── tasks/              # Reusable tasks
├── configs/                # Infrastructure definitions (edit these)
│   └── *.yml              # Configuration files
└── docs/                   # Documentation
    ├── ARCHITECTURE.md
    ├── CONFIGURATION_GUIDE.md
    ├── CONTRIBUTING.md
    ├── EXAMPLES.md
    ├── TROUBLESHOOTING.md
    └── QUICK_REFERENCE.md (this file)
```

## Getting Help

1. **Documentation**: Check [docs/](../docs/) directory
2. **Examples**: See [docs/EXAMPLES.md](EXAMPLES.md)
3. **Troubleshooting**: See [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **AWS Documentation**: https://docs.aws.amazon.com/
5. **Ansible Documentation**: https://docs.ansible.com/

## Quick Links

- [README](../README.md) - Main documentation
- [Configuration Guide](CONFIGURATION_GUIDE.md) - Detailed config reference
- [Architecture](ARCHITECTURE.md) - Design documentation
- [Examples](EXAMPLES.md) - Usage examples
- [Troubleshooting](TROUBLESHOOTING.md) - Problem solving
- [Contributing](CONTRIBUTING.md) - How to contribute
