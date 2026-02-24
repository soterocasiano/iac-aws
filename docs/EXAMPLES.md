# Examples

This document provides complete, ready-to-use examples for common infrastructure scenarios.

## Example 1: Simple Web Application Infrastructure

This example creates a complete VPC with public subnets, an EC2 web server, and an S3 bucket.

### Configuration Files

**configs/vpc.yml**
```yaml
webapp-vpc:
  - name: webapp-vpc
    region: us-east-1
    cidr_block: 10.0.0.0/16
```

**configs/vpc-subnets.yml**
```yaml
webapp-subnets:
  - name: webapp-public-subnet-1a
    vpc_name: webapp-vpc
    cidr_block: 10.0.1.0/24
    az: us-east-1a
    region: us-east-1
    map_public: true
    tags:
      Name: webapp-public-subnet-1a
      Type: public

  - name: webapp-public-subnet-1b
    vpc_name: webapp-vpc
    cidr_block: 10.0.2.0/24
    az: us-east-1b
    region: us-east-1
    map_public: true
    tags:
      Name: webapp-public-subnet-1b
      Type: public
```

**configs/vpc-internet-gateways.yml**
```yaml
webapp-igw:
  - vpc_name: webapp-vpc
    region: us-east-1
    tags:
      Name: webapp-vpc-igw
```

**configs/vpc-route-tables.yml**
```yaml
webapp-route-tables:
  - name: webapp-public-rt
    vpc_name: webapp-vpc
    region: us-east-1
    subnets:
      - webapp-public-subnet-1a
      - webapp-public-subnet-1b
    routes:
      - dest: 0.0.0.0/0
        gateway_id: webapp-vpc-igw
    tags:
      Name: webapp-public-rt
```

**configs/vpc-security-groups.yml**
```yaml
webapp-security-groups:
  - name: webapp-web-sg
    vpc_name: webapp-vpc
    region: us-east-1
    description: "Security group for web servers"
    rules:
      - proto: tcp
        from_port: 80
        to_port: 80
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTP from internet"
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTPS from internet"
      - proto: tcp
        from_port: 22
        to_port: 22
        cidr_ip: 1.2.3.4/32  # Replace with your IP
        rule_desc: "Allow SSH from admin IP"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow all outbound"
    tags:
      Name: webapp-web-sg
```

**configs/iam-roles.yml**
```yaml
webapp-roles:
  - name: webapp-ec2-role
    assume_role_policy_document:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Service: ec2.amazonaws.com
          Action: sts:AssumeRole
    managed_policies:
      - arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
      - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
    tags:
      Application: webapp
```

**configs/iam-instance-profiles.yml**
```yaml
webapp-profiles:
  - name: webapp-instance-profile
    role_name: webapp-ec2-role
    tags:
      Application: webapp
```

**configs/ec2-instances.yml**
```yaml
webapp-instances:
  - name: webapp-server-1
    instance_type: t3.micro
    image_id: ami-0c55b159cbfafe1f0  # Amazon Linux 2 (us-east-1)
    region: us-east-1
    vpc_subnet_id: webapp-public-subnet-1a
    security_groups:
      - webapp-web-sg
    key_name: my-keypair  # Replace with your key pair name
    iam_instance_profile: webapp-instance-profile
    user_data: |
      #!/bin/bash
      yum update -y
      yum install -y httpd
      systemctl start httpd
      systemctl enable httpd
      echo "<h1>Hello from Web App Server</h1>" > /var/www/html/index.html
    tags:
      Name: webapp-server-1
      Environment: production
      Application: webapp
```

**configs/s3-buckets.yml**
```yaml
webapp-buckets:
  - name: webapp-static-assets-12345  # Replace with unique name
    region: us-east-1
    versioning: true
    encryption: AES256
    public_access:
      block_public_acls: true
      block_public_policy: true
      ignore_public_acls: true
      restrict_public_buckets: true
    tags:
      Application: webapp
      Environment: production
```

### Deployment

```bash
cd automation

# Deploy infrastructure in order
ansible-playbook iac-vpc.yml
ansible-playbook iac-iam.yml
ansible-playbook iac-ec2.yml
ansible-playbook iac-s3.yml
```

### Teardown

```bash
cd automation
ansible-playbook iac-teardown.yml -e confirm_teardown=yes
```

---

## Example 2: Three-Tier Architecture with Private Subnets

This example creates a VPC with public and private subnets, NAT gateways, and proper routing for a three-tier application.

### Configuration Files

**configs/vpc.yml**
```yaml
threetier-vpc:
  - name: threetier-vpc
    region: us-east-1
    cidr_block: 10.100.0.0/16
```

**configs/vpc-subnets.yml**
```yaml
threetier-subnets:
  # Public subnets (web tier)
  - name: threetier-public-web-1a
    vpc_name: threetier-vpc
    cidr_block: 10.100.1.0/24
    az: us-east-1a
    region: us-east-1
    map_public: true
    tags:
      Name: threetier-public-web-1a
      Tier: web

  - name: threetier-public-web-1b
    vpc_name: threetier-vpc
    cidr_block: 10.100.2.0/24
    az: us-east-1b
    region: us-east-1
    map_public: true
    tags:
      Name: threetier-public-web-1b
      Tier: web

  # Private subnets (app tier)
  - name: threetier-private-app-1a
    vpc_name: threetier-vpc
    cidr_block: 10.100.11.0/24
    az: us-east-1a
    region: us-east-1
    map_public: false
    tags:
      Name: threetier-private-app-1a
      Tier: app

  - name: threetier-private-app-1b
    vpc_name: threetier-vpc
    cidr_block: 10.100.12.0/24
    az: us-east-1b
    region: us-east-1
    map_public: false
    tags:
      Name: threetier-private-app-1b
      Tier: app

  # Private subnets (database tier)
  - name: threetier-private-db-1a
    vpc_name: threetier-vpc
    cidr_block: 10.100.21.0/24
    az: us-east-1a
    region: us-east-1
    map_public: false
    tags:
      Name: threetier-private-db-1a
      Tier: database

  - name: threetier-private-db-1b
    vpc_name: threetier-vpc
    cidr_block: 10.100.22.0/24
    az: us-east-1b
    region: us-east-1
    map_public: false
    tags:
      Name: threetier-private-db-1b
      Tier: database
```

**configs/vpc-internet-gateways.yml**
```yaml
threetier-igw:
  - vpc_name: threetier-vpc
    region: us-east-1
    tags:
      Name: threetier-vpc-igw
```

**configs/vpc-nat-gateways.yml**
```yaml
threetier-nat:
  - subnet_name: threetier-public-web-1a
    region: us-east-1
    tags:
      Name: threetier-nat-1a

  - subnet_name: threetier-public-web-1b
    region: us-east-1
    tags:
      Name: threetier-nat-1b
```

**configs/vpc-route-tables.yml**
```yaml
threetier-route-tables:
  # Public route table
  - name: threetier-public-rt
    vpc_name: threetier-vpc
    region: us-east-1
    subnets:
      - threetier-public-web-1a
      - threetier-public-web-1b
    routes:
      - dest: 0.0.0.0/0
        gateway_id: threetier-vpc-igw
    tags:
      Name: threetier-public-rt

  # Private route table for AZ 1a
  - name: threetier-private-rt-1a
    vpc_name: threetier-vpc
    region: us-east-1
    subnets:
      - threetier-private-app-1a
      - threetier-private-db-1a
    routes:
      - dest: 0.0.0.0/0
        nat_gateway_id: threetier-nat-1a
    tags:
      Name: threetier-private-rt-1a

  # Private route table for AZ 1b
  - name: threetier-private-rt-1b
    vpc_name: threetier-vpc
    region: us-east-1
    subnets:
      - threetier-private-app-1b
      - threetier-private-db-1b
    routes:
      - dest: 0.0.0.0/0
        nat_gateway_id: threetier-nat-1b
    tags:
      Name: threetier-private-rt-1b
```

**configs/vpc-security-groups.yml**
```yaml
threetier-security-groups:
  # Web tier security group
  - name: threetier-web-sg
    vpc_name: threetier-vpc
    region: us-east-1
    description: "Security group for web tier"
    rules:
      - proto: tcp
        from_port: 80
        to_port: 80
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTP from internet"
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTPS from internet"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow all outbound"
    tags:
      Name: threetier-web-sg
      Tier: web

  # App tier security group
  - name: threetier-app-sg
    vpc_name: threetier-vpc
    region: us-east-1
    description: "Security group for app tier"
    rules:
      - proto: tcp
        from_port: 8080
        to_port: 8080
        cidr_ip: 10.100.1.0/24
        rule_desc: "Allow 8080 from web subnet 1a"
      - proto: tcp
        from_port: 8080
        to_port: 8080
        cidr_ip: 10.100.2.0/24
        rule_desc: "Allow 8080 from web subnet 1b"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow all outbound"
    tags:
      Name: threetier-app-sg
      Tier: app

  # Database tier security group
  - name: threetier-db-sg
    vpc_name: threetier-vpc
    region: us-east-1
    description: "Security group for database tier"
    rules:
      - proto: tcp
        from_port: 3306
        to_port: 3306
        cidr_ip: 10.100.11.0/24
        rule_desc: "Allow MySQL from app subnet 1a"
      - proto: tcp
        from_port: 3306
        to_port: 3306
        cidr_ip: 10.100.12.0/24
        rule_desc: "Allow MySQL from app subnet 1b"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow all outbound"
    tags:
      Name: threetier-db-sg
      Tier: database
```

### Deployment

```bash
cd automation
ansible-playbook iac-vpc.yml
```

---

## Example 3: VPC Endpoints for S3 and EC2

This example shows how to create VPC endpoints to access AWS services without internet gateway.

**configs/vpc-endpoints.yml**
```yaml
my-endpoints:
  # Gateway endpoint for S3
  - service: s3
    vpc_name: my-vpc
    region: us-east-1
    route_table_ids:
      - my-private-rt-1a
      - my-private-rt-1b
    tags:
      Name: my-s3-gateway-endpoint

  # Gateway endpoint for DynamoDB
  - service: dynamodb
    vpc_name: my-vpc
    region: us-east-1
    route_table_ids:
      - my-private-rt-1a
      - my-private-rt-1b
    tags:
      Name: my-dynamodb-gateway-endpoint

  # Interface endpoint for EC2
  - service: ec2
    vpc_name: my-vpc
    region: us-east-1
    vpc_endpoint_type: Interface
    subnet_names:
      - my-private-subnet-1a
      - my-private-subnet-1b
    security_group_names:
      - my-endpoint-sg
    tags:
      Name: my-ec2-interface-endpoint
```

**Required: Endpoint Security Group**

**configs/vpc-security-groups.yml**
```yaml
endpoint-sg:
  - name: my-endpoint-sg
    vpc_name: my-vpc
    region: us-east-1
    description: "Security group for VPC interface endpoints"
    rules:
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 10.0.0.0/16
        rule_desc: "Allow HTTPS from VPC"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow all outbound"
    tags:
      Name: my-endpoint-sg
```

---

## Example 4: Multi-Region Deployment

This example shows how to deploy the same infrastructure to multiple regions.

**configs/vpc.yml**
```yaml
multi-region-vpcs:
  - name: app-vpc-us-east-1
    region: us-east-1
    cidr_block: 10.10.0.0/16

  - name: app-vpc-us-west-2
    region: us-west-2
    cidr_block: 10.20.0.0/16

  - name: app-vpc-eu-west-1
    region: eu-west-1
    cidr_block: 10.30.0.0/16
```

**configs/vpc-subnets.yml**
```yaml
multi-region-subnets:
  # US East 1
  - name: app-subnet-us-east-1a
    vpc_name: app-vpc-us-east-1
    cidr_block: 10.10.1.0/24
    az: us-east-1a
    region: us-east-1
    map_public: true
    tags:
      Name: app-subnet-us-east-1a

  # US West 2
  - name: app-subnet-us-west-2a
    vpc_name: app-vpc-us-west-2
    cidr_block: 10.20.1.0/24
    az: us-west-2a
    region: us-west-2
    map_public: true
    tags:
      Name: app-subnet-us-west-2a

  # EU West 1
  - name: app-subnet-eu-west-1a
    vpc_name: app-vpc-eu-west-1
    cidr_block: 10.30.1.0/24
    az: eu-west-1a
    region: eu-west-1
    map_public: true
    tags:
      Name: app-subnet-eu-west-1a
```

### Deployment

```bash
cd automation
ansible-playbook iac-vpc.yml
# Resources will be created in all specified regions
```

---

## Example 5: Development, Staging, and Production Environments

Organize configurations by environment.

### Directory Structure

```
configs/
├── dev/
│   ├── vpc.yml
│   ├── vpc-subnets.yml
│   └── ec2-instances.yml
├── staging/
│   ├── vpc.yml
│   ├── vpc-subnets.yml
│   └── ec2-instances.yml
└── prod/
    ├── vpc.yml
    ├── vpc-subnets.yml
    └── ec2-instances.yml
```

### Deployment

```bash
cd automation

# Deploy to dev
ansible-playbook iac-vpc.yml -e config_repo_dir=~/iac-aws/configs/dev

# Deploy to staging
ansible-playbook iac-vpc.yml -e config_repo_dir=~/iac-aws/configs/staging

# Deploy to production
ansible-playbook iac-vpc.yml -e config_repo_dir=~/iac-aws/configs/prod
```

---

## Tips for Configuration

1. **Start Small**: Begin with a simple VPC and gradually add complexity
2. **Test Incrementally**: Deploy and test each component before moving to the next
3. **Use Consistent Naming**: Follow a naming convention across all resources
4. **Tag Everything**: Use comprehensive tagging for cost allocation and management
5. **Document Custom Configs**: Add comments in YAML for complex configurations
6. **Version Control**: Keep all configurations in Git
7. **Separate Environments**: Use different config directories or files for dev/staging/prod
8. **Security First**: Always review security group rules and IAM policies
