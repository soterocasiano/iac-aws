#!/usr/bin/env python3
"""
Custom Ansible filter plugins for AWS operations.
"""

from ansible.errors import AnsibleFilterError

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


def get_subnet_id_by_name(subnet_name, region='us-east-1'):
    """
    Lookup a subnet ID by its Name tag using AWS API.

    Args:
        subnet_name: The value of the Name tag for the subnet
        region: AWS region (default: us-east-1)

    Returns:
        The subnet ID if found, None otherwise
    """
    if not HAS_BOTO3:
        raise AnsibleFilterError("boto3 is required for get_subnet_id_by_name filter")

    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [subnet_name]
                }
            ]
        )

        subnets = response.get('Subnets', [])
        if subnets:
            return subnets[0]['SubnetId']
        return None

    except ClientError as e:
        raise AnsibleFilterError(f"AWS API error: {e}")


def get_subnet_ids_by_names(subnet_names, region='us-east-1'):
    """
    Lookup multiple subnet IDs by their Name tags using AWS API.

    Args:
        subnet_names: List of Name tag values for subnets
        region: AWS region (default: us-east-1)

    Returns:
        List of subnet IDs
    """
    if not HAS_BOTO3:
        raise AnsibleFilterError("boto3 is required for get_subnet_ids_by_names filter")

    if not subnet_names:
        return []

    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': subnet_names
                }
            ]
        )

        subnets = response.get('Subnets', [])
        # Create a mapping of Name -> SubnetId
        name_to_id = {}
        for subnet in subnets:
            for tag in subnet.get('Tags', []):
                if tag['Key'] == 'Name':
                    name_to_id[tag['Value']] = subnet['SubnetId']
                    break

        # Return IDs in the same order as input names
        return [name_to_id.get(name) for name in subnet_names if name_to_id.get(name)]

    except ClientError as e:
        raise AnsibleFilterError(f"AWS API error: {e}")


class FilterModule:
    """Ansible filter plugin for AWS operations."""

    def filters(self):
        return {
            'get_subnet_id_by_name': get_subnet_id_by_name,
            'get_subnet_ids_by_names': get_subnet_ids_by_names,
        }
