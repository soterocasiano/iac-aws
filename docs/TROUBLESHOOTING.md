# Troubleshooting Guide

This guide helps you diagnose and fix common issues when using the iac-aws repository.

## Table of Contents

- [AWS Credentials Issues](#aws-credentials-issues)
- [Ansible Installation Issues](#ansible-installation-issues)
- [Module Not Found Errors](#module-not-found-errors)
- [Resource Creation Failures](#resource-creation-failures)
- [Custom Filter Errors](#custom-filter-errors)
- [Network Connectivity Issues](#network-connectivity-issues)
- [Teardown Issues](#teardown-issues)
- [Performance Issues](#performance-issues)
- [Debugging Tips](#debugging-tips)

## AWS Credentials Issues

### Error: "Unable to locate credentials"

**Symptoms:**
```
fatal: [localhost]: FAILED! => {"msg": "Unable to locate credentials"}
```

**Cause:** AWS credentials are not configured or not accessible to Ansible.

**Solutions:**

1. **Configure AWS CLI:**
   ```bash
   aws configure
   ```
   Enter your Access Key ID, Secret Access Key, and default region.

2. **Use Environment Variables:**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Verify Credentials:**
   ```bash
   aws sts get-caller-identity
   ```
   This should return your AWS account information.

4. **Check Credential File:**
   ```bash
   cat ~/.aws/credentials
   cat ~/.aws/config
   ```

### Error: "Access Denied" or "UnauthorizedOperation"

**Cause:** IAM user/role lacks required permissions.

**Solution:**

1. Verify IAM permissions for the user/role:
   - VPC: `ec2:*`
   - IAM: `iam:*`
   - S3: `s3:*`
   - Or use AWS managed policies: `PowerUserAccess` or `AdministratorAccess`

2. Check for Service Control Policies (SCPs) that might restrict actions.

3. Verify you're in the correct AWS account:
   ```bash
   aws sts get-caller-identity
   ```

## Ansible Installation Issues

### Error: "ansible-playbook: command not found"

**Cause:** Ansible is not installed or not in PATH.

**Solution:**

```bash
# Install Ansible
pip install ansible-core==2.16.14

# Verify installation
ansible-playbook --version
```

### Error: Python version incompatibility

**Cause:** Python version is too old or too new for Ansible 2.16.

**Solution:**

```bash
# Check Python version
python --version

# Ansible 2.16 requires Python 3.6+
# If using older version, upgrade Python:
# Ubuntu/Debian:
sudo apt-get install python3.9

# Use specific Python version with pip:
python3.9 -m pip install ansible-core==2.16.14
```

## Module Not Found Errors

### Error: "module amazon.aws.ec2_vpc_net not found"

**Cause:** Ansible collections are not installed.

**Solution:**

```bash
# Install all required collections
cd automation
ansible-galaxy collection install -r setup/requirements.yml

# Verify collections are installed
ansible-galaxy collection list | grep amazon.aws
```

### Error: "ModuleNotFoundError: No module named 'boto3'"

**Cause:** Python boto3 library is not installed.

**Solution:**

```bash
# Install Python dependencies
cd automation
pip install -r setup/requirements.txt

# Verify boto3 installation
python -c "import boto3; print(boto3.__version__)"
```

## Resource Creation Failures

### Error: "VPC not found" when creating subnets

**Cause:** VPC doesn't exist or name resolution failed.

**Solutions:**

1. **Ensure VPC is created first:**
   ```bash
   ansible-playbook iac-vpc.yml --tags vpc
   ```

2. **Verify VPC exists:**
   ```bash
   aws ec2 describe-vpcs --filters "Name=tag:Name,Values=my-vpc-name"
   ```

3. **Check VPC name in config matches:**
   Review `configs/vpc.yml` and `configs/vpc-subnets.yml` to ensure names match exactly.

### Error: "InvalidSubnet.Range" or CIDR overlap

**Cause:** Subnet CIDR blocks overlap or are outside VPC CIDR.

**Solution:**

1. **Review CIDR allocation:**
   - VPC: 10.0.0.0/16
   - Subnet 1: 10.0.1.0/24 ✓
   - Subnet 2: 10.0.2.0/24 ✓
   - Subnet 3: 10.0.1.0/24 ✗ (overlaps with Subnet 1)
   - Subnet 4: 192.168.0.0/24 ✗ (outside VPC CIDR)

2. **Use CIDR calculator:**
   ```
   VPC: 10.0.0.0/16 provides 10.0.0.0 - 10.0.255.255
   Subnets should be within this range
   ```

### Error: "RouteAlreadyExists"

**Cause:** Multiple route tables trying to add the same route.

**Solution:**

1. Check route table configurations for duplicates
2. Ensure each route table has unique subnet associations
3. Remove duplicate route entries

### Error: "DependencyViolation" when creating resources

**Cause:** Resource dependencies not satisfied (e.g., trying to create NAT gateway before subnet).

**Solution:**

Run playbooks in dependency order:
```bash
# Correct order:
ansible-playbook iac-vpc.yml    # Creates VPC, IGW, Subnets, NAT, Routes, etc.
ansible-playbook iac-iam.yml    # Creates IAM resources
ansible-playbook iac-ec2.yml    # Creates EC2 instances
ansible-playbook iac-s3.yml     # Creates S3 buckets
```

### Error: "Bucket name already exists" for S3

**Cause:** S3 bucket names must be globally unique across all AWS accounts.

**Solution:**

Add a unique suffix to bucket names:
```yaml
my-buckets:
  - name: my-app-bucket-12345-unique-id  # Add unique identifier
    region: us-east-1
```

## Custom Filter Errors

### Error: "filter get_aws_resource_id not found"

**Cause:** Custom filter plugin not loaded.

**Solutions:**

1. **Verify plugin file exists:**
   ```bash
   ls -la automation/plugins/filter/aws_filters.py
   ```

2. **Check ansible.cfg:**
   ```bash
   cat automation/ansible.cfg
   ```
   Should include:
   ```ini
   [defaults]
   filter_plugins = ./plugins/filter
   ```

3. **Check Python syntax in filter:**
   ```bash
   python automation/plugins/filter/aws_filters.py
   ```

### Error: "Resource not found" from custom filter

**Cause:** Filter cannot find AWS resource by name tag.

**Solutions:**

1. **Verify resource exists:**
   ```bash
   # For VPC:
   aws ec2 describe-vpcs --filters "Name=tag:Name,Values=my-vpc-name"
   
   # For Subnet:
   aws ec2 describe-subnets --filters "Name=tag:Name,Values=my-subnet-name"
   ```

2. **Check Name tag is set correctly:**
   Resources must have a "Name" tag matching the configuration.

3. **Verify region:**
   Ensure you're looking in the correct AWS region.

4. **Enable verbose mode:**
   ```bash
   ansible-playbook iac-vpc.yml -vvv
   ```
   This shows the boto3 API calls and responses.

## Network Connectivity Issues

### Error: "Connection timeout" to EC2 instance

**Cause:** Security group or NACL blocking traffic, or instance not running.

**Solutions:**

1. **Check security group rules:**
   ```bash
   aws ec2 describe-security-groups --group-ids sg-12345678
   ```

2. **Check NACL rules:**
   ```bash
   aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=subnet-12345678"
   ```

3. **Verify route table:**
   Ensure route table has route to internet gateway (for public subnets) or NAT gateway (for private subnets).

4. **Check instance state:**
   ```bash
   aws ec2 describe-instances --instance-ids i-12345678
   ```

### Error: Private subnet instances cannot access internet

**Cause:** NAT gateway not configured or route table incorrect.

**Solutions:**

1. **Verify NAT gateway exists:**
   ```bash
   aws ec2 describe-nat-gateways --filter "Name=subnet-id,Values=subnet-12345678"
   ```

2. **Check route table:**
   Private subnet route table should have route to NAT gateway:
   ```yaml
   routes:
     - dest: 0.0.0.0/0
       nat_gateway_id: my-nat-gateway-name
   ```

3. **Verify NAT gateway state:**
   ```bash
   aws ec2 describe-nat-gateways --nat-gateway-ids nat-12345678
   ```
   State should be "available".

## Teardown Issues

### Error: "DependencyViolation" during teardown

**Cause:** Resources have dependencies that must be deleted first.

**Solution:**

Use the teardown playbook which deletes in correct order:
```bash
cd automation
ansible-playbook iac-teardown.yml -e confirm_teardown=yes
```

If manual deletion needed:
1. Delete EC2 instances
2. Delete NAT gateways
3. Delete VPC endpoints
4. Delete subnets
5. Delete route tables
6. Delete security groups
7. Delete NACLs
8. Delete internet gateways
9. Delete VPC

### Error: "Resource in use" when deleting

**Cause:** Resource is still attached or in use.

**Solution:**

1. **For VPC:** Delete all resources within VPC first
2. **For Subnet:** Terminate instances, delete ENIs
3. **For Security Group:** Remove from instances, delete referencing rules in other SGs
4. **For Route Table:** Disassociate from subnets
5. **For Internet Gateway:** Detach from VPC

Check dependencies:
```bash
# Find ENIs in subnet:
aws ec2 describe-network-interfaces --filters "Name=subnet-id,Values=subnet-12345678"

# Find instances using security group:
aws ec2 describe-instances --filters "Name=instance.group-id,Values=sg-12345678"
```

## Performance Issues

### Slow playbook execution

**Cause:** Many resources or slow API calls.

**Solutions:**

1. **Use tags to run specific plays:**
   ```bash
   ansible-playbook iac-vpc.yml --tags vpc-subnets
   ```

2. **Increase parallelism:**
   ```bash
   ansible-playbook iac-vpc.yml -f 10
   ```

3. **Reduce API calls:**
   - Batch operations where possible
   - Use filters to reduce boto3 describe calls

4. **Enable SSH pipelining** (in ansible.cfg):
   ```ini
   [defaults]
   pipelining = True
   ```

### Rate limiting errors

**Cause:** AWS API throttling due to too many requests.

**Solution:**

1. **Add delays between tasks:**
   ```yaml
   - name: Wait between resource creation
     ansible.builtin.pause:
       seconds: 5
   ```

2. **Request AWS support to increase API limits**

3. **Reduce concurrent playbook runs**

## Debugging Tips

### Enable Verbose Output

```bash
# Level 1: Shows task results
ansible-playbook iac-vpc.yml -v

# Level 2: Shows task input/output
ansible-playbook iac-vpc.yml -vv

# Level 3: Shows connection debugging
ansible-playbook iac-vpc.yml -vvv

# Level 4: Shows everything including SSH details
ansible-playbook iac-vpc.yml -vvvv
```

### Check Mode (Dry Run)

```bash
# See what would change without making changes
ansible-playbook iac-vpc.yml --check

# Show diffs of what would change
ansible-playbook iac-vpc.yml --check --diff
```

### Step Mode

```bash
# Confirm each task before running
ansible-playbook iac-vpc.yml --step
```

### Start at Specific Task

```bash
# Resume from a specific task
ansible-playbook iac-vpc.yml --start-at-task="Create a VPC"
```

### Test Single Task

Create a test playbook:
```yaml
---
- hosts: localhost
  gather_facts: false
  tasks:
    - name: Test VPC creation
      amazon.aws.ec2_vpc_net:
        name: test-vpc
        cidr_block: 10.0.0.0/16
        region: us-east-1
        state: present
      register: result

    - name: Show result
      debug:
        var: result
```

### Debug Variables

Add debug tasks:
```yaml
- name: Debug loaded config
  debug:
    var: desired_vpcs
    verbosity: 0
```

### Check Configuration Syntax

```bash
# Validate YAML syntax
yamllint configs/

# Check playbook syntax
ansible-playbook iac-vpc.yml --syntax-check
```

### AWS CLI Verification

Always verify via AWS CLI:
```bash
# List VPCs
aws ec2 describe-vpcs

# List subnets
aws ec2 describe-subnets

# List security groups
aws ec2 describe-security-groups

# List running instances
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"
```

### Check Ansible Configuration

```bash
# Show Ansible configuration
ansible-config dump

# Show configuration files being used
ansible-config view

# List where config values come from
ansible-config list
```

## Getting Help

If you're still experiencing issues:

1. **Check AWS Service Health:**
   - Visit https://status.aws.amazon.com/

2. **Review AWS CloudTrail:**
   - Check for API errors in CloudTrail logs

3. **Search GitHub Issues:**
   - Check if similar issues exist in ansible-collections/amazon.aws

4. **Enable AWS CLI Debug:**
   ```bash
   aws ec2 describe-vpcs --debug
   ```

5. **Collect Information:**
   - Ansible version: `ansible-playbook --version`
   - Python version: `python --version`
   - Boto3 version: `python -c "import boto3; print(boto3.__version__)"`
   - AWS region: `echo $AWS_DEFAULT_REGION`
   - Error message and full stack trace
   - Configuration files (sanitized)

6. **Open an Issue:**
   - Provide all information above
   - Include minimal reproducible example
   - Sanitize any sensitive data (account IDs, IPs, etc.)
