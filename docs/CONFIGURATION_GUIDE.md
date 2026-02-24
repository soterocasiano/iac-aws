# Configuration Guide

This guide provides detailed information about configuring infrastructure resources in the `configs/` directory.

## Configuration File Structure

All configuration files follow a common pattern:

```yaml
resource-group-name:
  - name: resource-name-1
    # resource-specific properties
  - name: resource-name-2
    # resource-specific properties
```

Each top-level key represents a logical grouping of resources, and the value is a list of resource definitions.

## VPC Configuration

### VPCs (`configs/vpc.yml`)

Define Virtual Private Clouds.

```yaml
my-vpc-group:
  - name: my-vpc
    region: us-east-1
    cidr_block: 10.0.0.0/16
```

**Fields:**
- `name` (required): VPC name, used for tagging and reference
- `region` (required): AWS region (e.g., us-east-1, us-west-2)
- `cidr_block` (required): IPv4 CIDR block for the VPC

### Subnets (`configs/vpc-subnets.yml`)

Define subnets within VPCs.

```yaml
my-subnet-group:
  - name: my-public-subnet-1a
    vpc_name: my-vpc
    cidr_block: 10.0.1.0/24
    az: us-east-1a
    region: us-east-1
    map_public: true
    tags:
      Name: my-public-subnet-1a
      Type: public

  - name: my-private-subnet-1a
    vpc_name: my-vpc
    cidr_block: 10.0.10.0/24
    az: us-east-1a
    region: us-east-1
    map_public: false
    tags:
      Name: my-private-subnet-1a
      Type: private
```

**Fields:**
- `name` (required): Subnet name
- `vpc_name` (required): Name of the VPC to create subnet in
- `cidr_block` (required): IPv4 CIDR block for the subnet
- `az` (required): Availability zone (e.g., us-east-1a)
- `region` (required): AWS region
- `map_public` (optional): Auto-assign public IP addresses (true/false)
- `tags` (optional): AWS resource tags

### Internet Gateways (`configs/vpc-internet-gateways.yml`)

Define Internet Gateways for VPCs.

```yaml
my-igw-group:
  - vpc_name: my-vpc
    region: us-east-1
    tags:
      Name: my-vpc-igw
```

**Fields:**
- `vpc_name` (required): Name of the VPC to attach to
- `region` (required): AWS region
- `tags` (required): AWS resource tags, should include Name tag

### NAT Gateways (`configs/vpc-nat-gateways.yml`)

Define NAT Gateways for private subnet internet access.

```yaml
my-nat-group:
  - subnet_name: my-public-subnet-1a
    region: us-east-1
    tags:
      Name: my-nat-1a
```

**Fields:**
- `subnet_name` (required): Name of public subnet to place NAT gateway in
- `region` (required): AWS region
- `tags` (required): AWS resource tags

### Route Tables (`configs/vpc-route-tables.yml`)

Define routing tables and associate with subnets.

```yaml
my-route-table-group:
  - name: my-public-rt
    vpc_name: my-vpc
    region: us-east-1
    subnets:
      - my-public-subnet-1a
      - my-public-subnet-1b
    routes:
      - dest: 0.0.0.0/0
        gateway_id: my-vpc-igw  # IGW name, will be resolved to ID
    tags:
      Name: my-public-rt

  - name: my-private-rt
    vpc_name: my-vpc
    region: us-east-1
    subnets:
      - my-private-subnet-1a
    routes:
      - dest: 0.0.0.0/0
        nat_gateway_id: my-nat-1a  # NAT gateway name, will be resolved
    tags:
      Name: my-private-rt
```

**Fields:**
- `name` (required): Route table name
- `vpc_name` (required): VPC name
- `region` (required): AWS region
- `subnets` (required): List of subnet names to associate
- `routes` (required): List of route definitions
  - `dest`: Destination CIDR block
  - `gateway_id`: Internet gateway name (for IGW routes)
  - `nat_gateway_id`: NAT gateway name (for NAT routes)
  - `vpc_peering_connection_id`: Peering connection ID
- `tags` (optional): AWS resource tags

### Network ACLs (`configs/vpc-network-acls.yml`)

Define Network Access Control Lists.

```yaml
my-nacl-group:
  - name: my-public-nacl
    vpc_name: my-vpc
    region: us-east-1
    subnets:
      - my-public-subnet-1a
    ingress:
      - [100, 'tcp', 'allow', '0.0.0.0/0', null, null, 80, 80]
      - [110, 'tcp', 'allow', '0.0.0.0/0', null, null, 443, 443]
      - [120, 'tcp', 'allow', '0.0.0.0/0', null, null, 22, 22]
      - [130, 'tcp', 'allow', '0.0.0.0/0', null, null, 1024, 65535]
    egress:
      - [100, 'all', 'allow', '0.0.0.0/0', null, null, null, null]
    tags:
      Name: my-public-nacl
```

**Fields:**
- `name` (required): NACL name
- `vpc_name` (required): VPC name
- `region` (required): AWS region
- `subnets` (required): List of subnet names to associate
- `ingress` (required): List of ingress rules [rule_num, protocol, allow/deny, cidr, icmp_type, icmp_code, from_port, to_port]
- `egress` (required): List of egress rules (same format as ingress)
- `tags` (optional): AWS resource tags

### Security Groups (`configs/vpc-security-groups.yml`)

Define Security Groups for instances.

```yaml
my-sg-group:
  - name: my-web-sg
    vpc_name: my-vpc
    region: us-east-1
    description: "Security group for web servers"
    rules:
      - proto: tcp
        from_port: 80
        to_port: 80
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTP from anywhere"
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow HTTPS from anywhere"
      - proto: tcp
        from_port: 22
        to_port: 22
        cidr_ip: 10.0.0.0/16
        rule_desc: "Allow SSH from VPC"
    rules_egress:
      - proto: all
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
        rule_desc: "Allow all outbound"
    tags:
      Name: my-web-sg
```

**Fields:**
- `name` (required): Security group name
- `vpc_name` (required): VPC name
- `region` (required): AWS region
- `description` (required): Security group description
- `rules` (optional): List of ingress rules
  - `proto`: Protocol (tcp, udp, icmp, all)
  - `from_port`: Starting port
  - `to_port`: Ending port
  - `cidr_ip`: Source CIDR block
  - `rule_desc`: Rule description
- `rules_egress` (optional): List of egress rules (same format)
- `tags` (optional): AWS resource tags

### VPC Endpoints (`configs/vpc-endpoints.yml`)

Define VPC Endpoints for AWS services.

```yaml
my-endpoint-group:
  # Gateway endpoint (S3, DynamoDB)
  - service: s3
    vpc_name: my-vpc
    region: us-east-1
    route_table_ids:
      - my-private-rt
    tags:
      Name: my-s3-endpoint

  # Interface endpoint
  - service: ec2
    vpc_name: my-vpc
    region: us-east-1
    vpc_endpoint_type: Interface
    subnet_names:
      - my-private-subnet-1a
    security_group_names:
      - my-endpoint-sg
    tags:
      Name: my-ec2-endpoint
```

**Fields:**
- `service` (required): AWS service name (s3, dynamodb, ec2, etc.)
- `vpc_name` (required): VPC name
- `region` (required): AWS region
- `vpc_endpoint_type` (optional): Gateway or Interface (default: Gateway)
- `route_table_ids` (for Gateway): List of route table names
- `subnet_names` (for Interface): List of subnet names
- `security_group_names` (for Interface): List of security group names
- `tags` (optional): AWS resource tags

## EC2 Configuration

### EC2 Instances (`configs/ec2-instances.yml`)

Define EC2 instances.

```yaml
my-instance-group:
  - name: my-web-server
    instance_type: t3.micro
    image_id: ami-0c55b159cbfafe1f0
    region: us-east-1
    vpc_subnet_id: my-public-subnet-1a
    security_groups:
      - my-web-sg
    key_name: my-keypair
    iam_instance_profile: my-instance-profile
    user_data: |
      #!/bin/bash
      yum update -y
      yum install -y httpd
      systemctl start httpd
      systemctl enable httpd
    tags:
      Name: my-web-server
      Environment: production
```

**Fields:**
- `name` (required): Instance name
- `instance_type` (required): EC2 instance type (t3.micro, t3.small, etc.)
- `image_id` (required): AMI ID
- `region` (required): AWS region
- `vpc_subnet_id` (required): Subnet name to launch in
- `security_groups` (optional): List of security group names
- `key_name` (optional): SSH key pair name
- `iam_instance_profile` (optional): IAM instance profile name
- `user_data` (optional): User data script
- `tags` (optional): AWS resource tags

## IAM Configuration

### IAM Users (`configs/iam-users.yml`)

Define IAM users.

```yaml
my-user-group:
  - name: developer-user
    managed_policies:
      - arn:aws:iam::aws:policy/ReadOnlyAccess
    tags:
      Team: development
```

**Fields:**
- `name` (required): IAM user name
- `managed_policies` (optional): List of managed policy ARNs
- `tags` (optional): AWS resource tags

### IAM Roles (`configs/iam-roles.yml`)

Define IAM roles.

```yaml
my-role-group:
  - name: ec2-role
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
      Purpose: EC2 instances
```

**Fields:**
- `name` (required): IAM role name
- `assume_role_policy_document` (required): Trust policy document
- `managed_policies` (optional): List of managed policy ARNs
- `tags` (optional): AWS resource tags

### IAM Instance Profiles (`configs/iam-instance-profiles.yml`)

Define IAM instance profiles for EC2.

```yaml
my-profile-group:
  - name: my-instance-profile
    role_name: ec2-role
    tags:
      Purpose: EC2 instances
```

**Fields:**
- `name` (required): Instance profile name
- `role_name` (required): IAM role name to attach
- `tags` (optional): AWS resource tags

## S3 Configuration

### S3 Buckets (`configs/s3-buckets.yml`)

Define S3 buckets.

```yaml
my-bucket-group:
  - name: my-app-bucket-unique-name
    region: us-east-1
    versioning: true
    encryption: AES256
    public_access:
      block_public_acls: true
      block_public_policy: true
      ignore_public_acls: true
      restrict_public_buckets: true
    tags:
      Environment: production
      Application: my-app
```

**Fields:**
- `name` (required): S3 bucket name (must be globally unique)
- `region` (required): AWS region
- `versioning` (optional): Enable versioning (true/false)
- `encryption` (optional): Server-side encryption (AES256, aws:kms)
- `public_access` (optional): Block public access settings
- `tags` (optional): AWS resource tags

## Best Practices

1. **Naming Convention**: Use consistent naming (e.g., `{project}-{resource}-{az}`)
2. **Tagging**: Always include descriptive tags for cost allocation and management
3. **Region Consistency**: Keep related resources in the same region
4. **CIDR Planning**: Plan IP address ranges to avoid conflicts
5. **Security**: Follow least privilege principle for security groups and IAM
6. **Version Control**: Keep configuration files in version control
7. **Testing**: Test changes in a non-production environment first
8. **Documentation**: Document any custom configurations or special requirements

## Configuration Validation

Before running playbooks, validate your configuration:

1. **YAML Syntax**: Ensure YAML is properly formatted
   ```bash
   yamllint configs/
   ```

2. **Required Fields**: Verify all required fields are present

3. **Dependencies**: Ensure referenced resources exist (VPC names, subnet names, etc.)

4. **AWS Limits**: Check AWS service limits for your account

5. **Dry Run**: Use `--check` mode to see what would change
   ```bash
   ansible-playbook iac-vpc.yml --check
   ```
