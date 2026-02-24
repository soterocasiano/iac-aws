# Architecture and Design

This document describes the architecture and design principles of the iac-aws repository.

## Design Principles

### 1. Separation of Concerns

The repository separates three distinct layers:

- **Configuration Layer** (`configs/`): Infrastructure definitions in YAML
- **Automation Layer** (`automation/`): Ansible playbooks and tasks
- **Plugin Layer** (`automation/plugins/`): Custom filters and modules

This separation allows:
- Infrastructure definitions to be version controlled independently
- Automation logic to be reused across different infrastructure definitions
- Easy testing and validation of configurations

### 2. Declarative Configuration

All infrastructure is defined declaratively in YAML configuration files. This means:
- You describe the desired state, not the steps to achieve it
- Playbooks are idempotent - running them multiple times produces the same result
- Easy to understand and review infrastructure changes

### 3. Modular Design

Resources are organized into logical modules:
- VPC infrastructure (networking)
- IAM (identity and access management)
- EC2 (compute instances)
- S3 (object storage)

Each module can be executed independently or combined as needed.

### 4. Resource Name Resolution

Custom Jinja2 filters automatically resolve resource names to AWS IDs:
- Configurations use human-readable names
- Filters query AWS API to find resource IDs
- Reduces hardcoding and improves maintainability

## Architecture Components

### Configuration Files

```
configs/
├── vpc.yml                      # VPC definitions
├── vpc-subnets.yml              # Subnet definitions
├── vpc-internet-gateways.yml    # IGW definitions
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

Each configuration file follows a consistent structure:
```yaml
resource-group-name:
  - resource-definition-1
  - resource-definition-2
```

### Playbooks

#### VPC Playbook (`iac-vpc.yml`)

Creates VPC infrastructure in dependency order:

1. **VPCs**: Create virtual private clouds
2. **Internet Gateways**: Attach IGWs to VPCs
3. **Subnets**: Create subnets in VPCs
4. **NAT Gateways**: Create NAT gateways in public subnets
5. **Route Tables**: Create route tables and associate with subnets
6. **Network ACLs**: Create NACLs and associate with subnets
7. **Security Groups**: Create security groups with rules
8. **VPC Endpoints**: Create VPC endpoints for AWS services

Each play is tagged for selective execution.

#### IAM Playbook (`iac-iam.yml`)

Creates IAM resources:

1. **Users**: Create IAM users with policies
2. **Roles**: Create IAM roles with trust policies
3. **Instance Profiles**: Create instance profiles for EC2

#### EC2 Playbook (`iac-ec2.yml`)

Creates EC2 instances with:
- Instance type and AMI
- Network placement (VPC, subnet)
- Security groups
- IAM instance profile
- User data scripts
- Tags

#### S3 Playbook (`iac-s3.yml`)

Creates S3 buckets with:
- Versioning
- Encryption
- Public access blocking
- Tags

#### Teardown Playbook (`iac-teardown.yml`)

Destroys resources in reverse dependency order with confirmation:

1. EC2 Instances
2. S3 Buckets
3. VPC Endpoints
4. Security Groups
5. Network ACLs
6. Route Tables
7. NAT Gateways
8. Subnets
9. Internet Gateways
10. VPCs
11. IAM Instance Profiles
12. IAM Roles
13. IAM Users

Requires `-e confirm_teardown=yes` to prevent accidental deletion.

### Custom Filters

Located in `automation/plugins/filter/aws_filters.py`:

#### `get_aws_resource_id(resource_name, resource_type, region)`

Resolves a single resource name to its AWS ID.

**Supported Resource Types:**
- `vpc`: VPC ID by Name tag
- `subnet`: Subnet ID by Name tag
- `security-group`: Security group ID by Name tag
- `internet-gateway`: IGW ID by Name tag
- `route-table`: Route table ID by Name tag
- `network-acl`: NACL ID by Name tag

**Example:**
```jinja2
{{ 'my-vpc' | get_aws_resource_id('vpc', 'us-east-1') }}
# Returns: vpc-12345678
```

#### `get_aws_resource_ids(resource_names, resource_type, region)`

Resolves multiple resource names to a list of AWS IDs.

**Example:**
```jinja2
{{ ['sg-web', 'sg-app'] | get_aws_resource_ids('security-group', 'us-east-1') }}
# Returns: ['sg-12345678', 'sg-87654321']
```

#### `resolve_route_gateway_ids(route, region)`

Resolves gateway names in route definitions to AWS IDs.

**Example:**
```jinja2
{{ route | resolve_route_gateway_ids('us-east-1') }}
# Input:  {dest: '0.0.0.0/0', gateway_id: 'my-igw'}
# Output: {dest: '0.0.0.0/0', gateway_id: 'igw-12345678'}
```

#### `get_nat_gateway_by_subnet(subnet_name, region)`

Gets NAT gateway ID by subnet name.

**Example:**
```jinja2
{{ 'my-public-subnet' | get_nat_gateway_by_subnet('us-east-1') }}
# Returns: nat-12345678
```

### Tasks

#### `copy_configs.yml`

Reusable task for loading configuration files.

**Variables:**
- `load_config_type`: Configuration file name (without .yml)
- `load_config_var`: Variable name to store loaded configuration

**Functionality:**
1. Constructs file path from `config_repo_dir` and `load_config_type`
2. Loads YAML file contents
3. Stores in variable specified by `load_config_var`

**Example Usage:**
```yaml
- name: Load Configs
  vars:
    load_config_type: vpc
    load_config_var: desired_vpcs
  ansible.builtin.include_tasks: tasks/copy_configs.yml
```

### Global Variables

Located in `automation/group_vars/all.yml`:

```yaml
iac_aws_dir: "~/personal/iac-aws"
config_repo_dir: "{{ iac_aws_dir }}/configs"
```

Defines the base directory and configuration directory path.

## Execution Flow

### Standard Flow

```
1. User defines infrastructure in configs/*.yml
   ↓
2. Playbook loads configuration via copy_configs.yml
   ↓
3. Playbook processes configuration with loops
   ↓
4. Custom filters resolve resource names to IDs
   ↓
5. Ansible modules call AWS APIs
   ↓
6. Resources created/updated in AWS
```

### Example: Creating a Subnet

```
1. configs/vpc-subnets.yml defines subnet with vpc_name: "my-vpc"
   ↓
2. iac-vpc.yml loads configuration into desired_subnets variable
   ↓
3. Playbook loops over desired_subnets
   ↓
4. Filter resolves "my-vpc" → "vpc-12345678"
   ↓
5. amazon.aws.ec2_vpc_subnet module called with vpc_id: "vpc-12345678"
   ↓
6. Subnet created in AWS
```

## Resource Dependencies

Understanding resource dependencies is critical for correct execution order:

### VPC Stack Dependencies

```
VPC
 ├─ Internet Gateway (depends on VPC)
 ├─ Subnet (depends on VPC)
 │   ├─ NAT Gateway (depends on Subnet - must be public)
 │   ├─ Route Table Association (depends on Route Table + Subnet)
 │   ├─ Network ACL Association (depends on NACL + Subnet)
 │   └─ EC2 Instance (depends on Subnet + Security Group)
 ├─ Route Table (depends on VPC)
 │   └─ Routes (depend on IGW or NAT Gateway)
 ├─ Network ACL (depends on VPC)
 ├─ Security Group (depends on VPC)
 └─ VPC Endpoint (depends on VPC, may depend on Route Tables or Subnets)
```

### IAM Dependencies

```
IAM Role
 └─ IAM Instance Profile (depends on Role)
     └─ EC2 Instance (depends on Instance Profile)
```

### Cross-Module Dependencies

- **EC2 Instances** depend on:
  - Subnets (VPC module)
  - Security Groups (VPC module)
  - IAM Instance Profiles (IAM module)

## Security Considerations

### Credential Management

- Never hardcode AWS credentials
- Use AWS credential chain:
  1. Environment variables
  2. AWS CLI configuration (~/.aws/credentials)
  3. IAM instance role (when running on EC2)

### Resource Isolation

- Use separate VPCs for different environments
- Use security groups to restrict traffic
- Use network ACLs for subnet-level filtering
- Use private subnets for sensitive resources

### IAM Best Practices

- Follow least privilege principle
- Use managed policies when possible
- Regularly audit IAM permissions
- Use IAM roles for EC2 instead of access keys

### Teardown Safety

- Requires explicit confirmation flag
- Destroys resources in safe dependency order
- Review resources before confirming teardown

## Scalability

### Multiple Environments

Create separate configuration sets for different environments:

```
configs/
├── prod/
│   ├── vpc.yml
│   ├── ec2-instances.yml
│   └── ...
├── staging/
│   ├── vpc.yml
│   ├── ec2-instances.yml
│   └── ...
└── dev/
    ├── vpc.yml
    ├── ec2-instances.yml
    └── ...
```

Update `config_repo_dir` in `group_vars/all.yml` or pass as extra var:
```bash
ansible-playbook iac-vpc.yml -e config_repo_dir=~/iac-aws/configs/prod
```

### Multiple Regions

Resources are configured per-region. To deploy to multiple regions:

1. Define resources with different regions in config files
2. Run playbooks (resources are created in specified regions)

Or:

1. Create region-specific configuration directories
2. Run playbooks for each region

### Large Scale Deployments

For large deployments:
- Use Ansible parallelism (`-f` flag)
- Break configuration into smaller chunks
- Use tags to execute specific plays
- Consider using Ansible Tower/AWX for orchestration

## Testing Strategy

### Configuration Validation

1. **Syntax Check**: Validate YAML syntax
   ```bash
   yamllint configs/
   ```

2. **Dry Run**: Use Ansible check mode
   ```bash
   ansible-playbook iac-vpc.yml --check
   ```

3. **Diff Mode**: See what would change
   ```bash
   ansible-playbook iac-vpc.yml --check --diff
   ```

### Infrastructure Testing

1. **Non-Production**: Test in dev/staging environment first
2. **Incremental**: Deploy one module at a time
3. **Validation**: Verify resources in AWS console
4. **Rollback**: Use teardown playbook if issues occur

## Maintenance

### Regular Tasks

1. **Update Dependencies**: Keep Ansible and collections updated
   ```bash
   pip install -U ansible-core boto3
   ansible-galaxy collection install -r automation/setup/requirements.yml --upgrade
   ```

2. **Review Configurations**: Audit configurations for unused resources

3. **Security Audit**: Review IAM policies and security groups

4. **Cost Optimization**: Review resource usage and costs

### Extending Functionality

To add new resource types:

1. Create configuration file in `configs/`
2. Create playbook or add play to existing playbook
3. Add custom filters if needed
4. Update documentation

Example: Adding RDS support:
1. Create `configs/rds-instances.yml`
2. Create `automation/iac-rds.yml`
3. Add RDS-specific filters if needed
4. Update README and configuration guide
