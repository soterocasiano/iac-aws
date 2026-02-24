# Contributing Guide

Thank you for your interest in contributing to the iac-aws project! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Making Changes](#making-changes)
- [Testing Your Changes](#testing-your-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)

## Code of Conduct

This project follows standard open-source community guidelines:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

### Prerequisites

1. **Fork the Repository:**
   - Click the "Fork" button on GitHub
   - Clone your fork locally:
     ```bash
     git clone https://github.com/YOUR-USERNAME/iac-aws.git
     cd iac-aws
     ```

2. **Set Up Upstream Remote:**
   ```bash
   git remote add upstream https://github.com/soterocasiano/iac-aws.git
   git fetch upstream
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r automation/setup/requirements.txt
   ansible-galaxy collection install -r automation/setup/requirements.yml
   ```

4. **Configure AWS:**
   - Set up a test AWS account (do not use production!)
   - Configure AWS credentials
   - Consider using AWS Organizations with a sandbox account

### Understanding the Codebase

Before making changes, familiarize yourself with:

1. **Repository Structure:**
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) for design overview
   - Review [README.md](../README.md) for basic usage

2. **Configuration Format:**
   - Study [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)
   - Look at existing configurations in `configs/`

3. **Custom Filters:**
   - Review `automation/plugins/filter/aws_filters.py`
   - Understand how resource name resolution works

## Development Workflow

### Creating a Feature Branch

Always create a new branch for your changes:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### Keeping Your Branch Updated

Regularly sync with upstream:

```bash
git fetch upstream
git rebase upstream/main
```

## Making Changes

### Types of Contributions

We welcome several types of contributions:

#### 1. Bug Fixes

If you find a bug:
1. Search existing issues to avoid duplicates
2. Create an issue describing the bug
3. Create a branch and fix the bug
4. Submit a pull request referencing the issue

#### 2. New Features

For new features:
1. Open an issue to discuss the feature first
2. Wait for maintainer feedback
3. Implement the feature after approval
4. Update documentation
5. Submit a pull request

#### 3. Documentation Improvements

Documentation contributions are always welcome:
- Fix typos or unclear sections
- Add examples
- Improve existing guides
- Add new guides for uncovered topics

#### 4. Configuration Examples

Share your infrastructure patterns:
- Add example configurations to `docs/EXAMPLES.md`
- Include context and use case
- Follow existing example format

### Adding New Resource Types

To add support for a new AWS resource type:

1. **Create Configuration File:**
   ```bash
   # Example: Adding RDS support
   touch configs/rds-instances.yml
   ```

2. **Define Configuration Structure:**
   ```yaml
   # configs/rds-instances.yml
   my-rds-group:
     - name: my-database
       engine: postgres
       instance_class: db.t3.micro
       allocated_storage: 20
       # ... other parameters
   ```

3. **Create or Update Playbook:**
   ```yaml
   # automation/iac-rds.yml
   ---
   - name: AWS RDS Instances
     hosts: localhost
     gather_facts: false
     tasks:
       - name: Load Configs
         vars:
           load_config_type: rds-instances
           load_config_var: desired_rds_instances
         ansible.builtin.include_tasks: tasks/copy_configs.yml

       - name: Create RDS Instances
         amazon.aws.rds_instance:
           # module parameters
         loop: '{{ desired_rds_instances.values() | list | flatten }}'
   ```

4. **Add Custom Filters (if needed):**
   ```python
   # automation/plugins/filter/aws_filters.py
   def get_rds_instance_id(instance_name, region):
       # Implementation
       pass
   ```

5. **Update Documentation:**
   - Add to README.md under "AWS Resources Managed"
   - Create section in CONFIGURATION_GUIDE.md
   - Add example to EXAMPLES.md

6. **Update Teardown Playbook:**
   Add resource deletion in appropriate order.

### Modifying Existing Resources

When modifying existing playbooks or configurations:

1. **Test Backward Compatibility:**
   - Ensure existing configurations still work
   - Don't break existing users' infrastructure

2. **Update Related Documentation:**
   - Configuration guide
   - Examples
   - Architecture documentation

3. **Consider Migration:**
   - If changing configuration format, provide migration guide
   - Support both old and new formats during transition

## Testing Your Changes

### Test Environment

**IMPORTANT:** Always test in a non-production AWS account!

1. **Create Separate Test Account:**
   - Use AWS Organizations for isolation
   - Set up billing alerts
   - Use restrictive SCPs

2. **Use Unique Resource Names:**
   ```yaml
   test-vpc:
     - name: test-myfeature-vpc-unique123
       # ...
   ```

### Testing Checklist

Before submitting changes:

- [ ] Syntax check passes
  ```bash
  ansible-playbook automation/iac-vpc.yml --syntax-check
  ```

- [ ] YAML linting passes (if available)
  ```bash
  yamllint configs/
  ```

- [ ] Dry run succeeds
  ```bash
  ansible-playbook automation/iac-vpc.yml --check
  ```

- [ ] Actual deployment succeeds
  ```bash
  ansible-playbook automation/iac-vpc.yml
  ```

- [ ] Resources created correctly
  ```bash
  aws ec2 describe-vpcs --filters "Name=tag:Name,Values=test-myfeature-vpc-unique123"
  ```

- [ ] Idempotency verified (run playbook twice, no changes on second run)
  ```bash
  ansible-playbook automation/iac-vpc.yml
  ansible-playbook automation/iac-vpc.yml  # Should show "ok" not "changed"
  ```

- [ ] Teardown succeeds
  ```bash
  ansible-playbook automation/iac-teardown.yml -e confirm_teardown=yes
  ```

- [ ] Documentation updated
- [ ] Examples added (if applicable)

### Manual Testing

1. **Deploy Test Infrastructure:**
   ```bash
   cd automation
   ansible-playbook iac-vpc.yml -e config_repo_dir=/path/to/test/configs
   ```

2. **Verify in AWS Console:**
   - Check resources are created correctly
   - Verify tags are applied
   - Test functionality (e.g., EC2 connectivity)

3. **Check Idempotency:**
   ```bash
   # Run again - should not make changes
   ansible-playbook iac-vpc.yml -e config_repo_dir=/path/to/test/configs
   ```

4. **Clean Up:**
   ```bash
   ansible-playbook iac-teardown.yml -e confirm_teardown=yes -e config_repo_dir=/path/to/test/configs
   ```

## Submitting Changes

### Commit Messages

Write clear, descriptive commit messages:

```
# Good commit messages:
Add support for RDS instance provisioning
Fix subnet CIDR calculation in custom filter
Update documentation for VPC endpoints

# Bad commit messages:
Update file
Fix bug
Changes
```

Format:
```
Brief summary (50 characters or less)

Detailed explanation if needed:
- What changed
- Why it changed
- Impact of the change

Fixes #123  # If fixing an issue
```

### Pull Request Process

1. **Update Your Branch:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to Your Fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request:**
   - Go to GitHub and click "New Pull Request"
   - Select your branch
   - Fill in the PR template (if available)

4. **PR Description Should Include:**
   - Summary of changes
   - Motivation and context
   - Testing performed
   - Screenshots (for UI changes)
   - Breaking changes (if any)
   - Related issues

5. **Example PR Description:**
   ```markdown
   ## Summary
   Adds support for RDS instance provisioning through new playbook and configuration files.

   ## Changes
   - Added `automation/iac-rds.yml` playbook
   - Created `configs/rds-instances.yml` configuration template
   - Updated `automation/iac-teardown.yml` to include RDS cleanup
   - Added RDS examples to documentation

   ## Testing
   - [x] Syntax check passed
   - [x] Deployed successfully to test account
   - [x] Verified RDS instance creation
   - [x] Tested teardown process
   - [x] Confirmed idempotency

   ## Documentation
   - Updated README.md
   - Added RDS section to CONFIGURATION_GUIDE.md
   - Added RDS example to EXAMPLES.md

   Closes #42
   ```

### Review Process

1. **Automated Checks:**
   - CI/CD pipeline runs (if configured)
   - Syntax validation
   - Linting checks

2. **Code Review:**
   - Maintainer reviews code
   - Feedback provided as comments
   - Address feedback promptly

3. **Revisions:**
   ```bash
   # Make changes based on feedback
   git add .
   git commit -m "Address review feedback"
   git push origin feature/your-feature-name
   ```

4. **Approval and Merge:**
   - Once approved, maintainer will merge
   - Delete your feature branch after merge

## Coding Standards

### Ansible Playbooks

1. **Use YAML Best Practices:**
   ```yaml
   # Good:
   - name: Create VPC
     amazon.aws.ec2_vpc_net:
       name: '{{ _vpc.name }}'
       cidr_block: '{{ _vpc.cidr_block }}'
       region: '{{ _vpc.region }}'
       state: present

   # Bad:
   - amazon.aws.ec2_vpc_net: name={{ _vpc.name }} cidr_block={{ _vpc.cidr_block }}
   ```

2. **Always Name Tasks:**
   ```yaml
   # Good:
   - name: Create Security Group
     amazon.aws.ec2_security_group:
       # ...

   # Bad:
   - amazon.aws.ec2_security_group:
       # ...
   ```

3. **Use Appropriate Variable Names:**
   - Prefix loop variables with underscore: `_vpc`, `_subnet`
   - Use descriptive names: `desired_vpcs`, not `vpcs`
   - Follow existing naming patterns

4. **Add Tags to Plays:**
   ```yaml
   - name: AWS VPC
     hosts: localhost
     gather_facts: false
     tags: [vpc]
     tasks:
       # ...
   ```

### Configuration Files

1. **Consistent Structure:**
   ```yaml
   resource-group-name:
     - name: resource-1
       # properties in consistent order
       region: us-east-1
       # ...
       tags:
         Name: resource-1
   ```

2. **Use Comments for Complex Config:**
   ```yaml
   # Production VPCs
   prod-vpcs:
     - name: prod-vpc-east
       # Using /16 to allow for future subnet expansion
       cidr_block: 10.0.0.0/16
   ```

3. **Meaningful Names:**
   - Use descriptive resource names
   - Follow naming convention: `{env}-{purpose}-{detail}`
   - Example: `prod-web-vpc`, `staging-app-subnet-1a`

### Python Code (Custom Filters)

1. **Follow PEP 8:**
   - Use 4 spaces for indentation
   - Maximum line length: 120 characters
   - Use docstrings

2. **Error Handling:**
   ```python
   def get_aws_resource_id(resource_name, resource_type, region):
       """Get AWS resource ID by name tag."""
       try:
           # Implementation
           return resource_id
       except ClientError as e:
           raise AnsibleFilterError(f"Error finding resource: {e}")
   ```

3. **Type Hints (optional):**
   ```python
   def get_aws_resource_id(resource_name: str, resource_type: str, region: str) -> str:
       # Implementation
   ```

## Documentation

### Documentation Requirements

All changes should include documentation updates:

1. **README.md:**
   - Update if adding new resource types
   - Update if changing usage

2. **CONFIGURATION_GUIDE.md:**
   - Document new configuration options
   - Provide field descriptions
   - Include examples

3. **EXAMPLES.md:**
   - Add practical examples
   - Show real-world use cases

4. **ARCHITECTURE.md:**
   - Update for architectural changes
   - Document new design patterns

5. **TROUBLESHOOTING.md:**
   - Add solutions for new issues discovered
   - Document common errors

### Documentation Style

1. **Use Clear Headings:**
   - Use markdown hierarchy (##, ###, ####)
   - Descriptive heading names

2. **Include Examples:**
   - Show both configuration and execution
   - Include expected output

3. **Code Blocks:**
   ```yaml
   # Always specify language for syntax highlighting
   resource-name:
     - property: value
   ```

4. **Be Concise but Complete:**
   - Don't assume knowledge
   - Explain "why" not just "how"
   - Link to related documentation

## Getting Help

### Questions

- Open a GitHub Discussion
- Comment on related issues
- Review existing documentation

### Stuck on Implementation

- Review similar existing code
- Check Ansible documentation
- Ask in pull request comments

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!
