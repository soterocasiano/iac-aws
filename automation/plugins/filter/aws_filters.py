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


# Mapping of resource types to their AWS describe methods and ID fields
RESOURCE_CONFIG = {
    'subnet': {
        'service': 'ec2',
        'method': 'describe_subnets',
        'response_key': 'Subnets',
        'id_field': 'SubnetId',
    },
    'vpc': {
        'service': 'ec2',
        'method': 'describe_vpcs',
        'response_key': 'Vpcs',
        'id_field': 'VpcId',
    },
    'internet_gateway': {
        'service': 'ec2',
        'method': 'describe_internet_gateways',
        'response_key': 'InternetGateways',
        'id_field': 'InternetGatewayId',
    },
    'nat_gateway': {
        'service': 'ec2',
        'method': 'describe_nat_gateways',
        'response_key': 'NatGateways',
        'id_field': 'NatGatewayId',
    },
    'security_group': {
        'service': 'ec2',
        'method': 'describe_security_groups',
        'response_key': 'SecurityGroups',
        'id_field': 'GroupId',
    },
    'route_table': {
        'service': 'ec2',
        'method': 'describe_route_tables',
        'response_key': 'RouteTables',
        'id_field': 'RouteTableId',
    },
    'network_acl': {
        'service': 'ec2',
        'method': 'describe_network_acls',
        'response_key': 'NetworkAcls',
        'id_field': 'NetworkAclId',
    },
    'instance': {
        'service': 'ec2',
        'method': 'describe_instances',
        'response_key': 'Reservations',
        'id_field': 'InstanceId',
        'nested_key': 'Instances',
    },
}


def get_aws_resource_id(name, resource_type, region='us-east-1'):
    """
    Lookup an AWS resource ID by its Name tag.

    Args:
        name: The value of the Name tag for the resource
        resource_type: Type of AWS resource (subnet, vpc, internet_gateway, etc.)
        region: AWS region (default: us-east-1)

    Returns:
        The resource ID if found, None otherwise
    """
    if not HAS_BOTO3:
        raise AnsibleFilterError("boto3 is required for get_aws_resource_id filter")

    if resource_type not in RESOURCE_CONFIG:
        raise AnsibleFilterError(
            f"Unsupported resource type: {resource_type}. "
            f"Supported types: {', '.join(RESOURCE_CONFIG.keys())}"
        )

    config = RESOURCE_CONFIG[resource_type]

    try:
        client = boto3.client(config['service'], region_name=region)
        method = getattr(client, config['method'])

        response = method(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [name]
                }
            ]
        )

        resources = response.get(config['response_key'], [])

        # Handle nested resources (like instances in reservations)
        if 'nested_key' in config:
            nested_resources = []
            for item in resources:
                nested_resources.extend(item.get(config['nested_key'], []))
            resources = nested_resources

        if resources:
            return resources[0][config['id_field']]
        return None

    except ClientError as e:
        raise AnsibleFilterError(f"AWS API error: {e}")


def get_aws_resource_ids(names, resource_type, region='us-east-1'):
    """
    Lookup multiple AWS resource IDs by their Name tags.

    Args:
        names: List of Name tag values for the resources
        resource_type: Type of AWS resource (subnet, vpc, internet_gateway, etc.)
        region: AWS region (default: us-east-1)

    Returns:
        List of resource IDs in the same order as input names
    """
    if not HAS_BOTO3:
        raise AnsibleFilterError("boto3 is required for get_aws_resource_ids filter")

    if not names:
        return []

    if resource_type not in RESOURCE_CONFIG:
        raise AnsibleFilterError(
            f"Unsupported resource type: {resource_type}. "
            f"Supported types: {', '.join(RESOURCE_CONFIG.keys())}"
        )

    config = RESOURCE_CONFIG[resource_type]

    try:
        client = boto3.client(config['service'], region_name=region)
        method = getattr(client, config['method'])

        response = method(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': names
                }
            ]
        )

        resources = response.get(config['response_key'], [])

        # Handle nested resources (like instances in reservations)
        if 'nested_key' in config:
            nested_resources = []
            for item in resources:
                nested_resources.extend(item.get(config['nested_key'], []))
            resources = nested_resources

        # Create a mapping of Name -> ResourceId
        name_to_id = {}
        for resource in resources:
            for tag in resource.get('Tags', []):
                if tag['Key'] == 'Name':
                    name_to_id[tag['Value']] = resource[config['id_field']]
                    break

        # Return IDs in the same order as input names
        return [name_to_id.get(name) for name in names if name_to_id.get(name)]

    except ClientError as e:
        raise AnsibleFilterError(f"AWS API error: {e}")


def resolve_route_gateway_ids(routes, region='us-east-1'):
    """
    Transform routes list by resolving gateway names to their IDs.

    Args:
        routes: List of route dictionaries with 'gateway_id' containing gateway Name tags
        region: AWS region (default: us-east-1)

    Returns:
        List of routes with gateway_id resolved to actual AWS gateway IDs
    """
    if not routes:
        return []

    resolved_routes = []
    for route in routes:
        resolved_route = route.copy()
        if 'gateway_id' in route and route['gateway_id']:
            gateway_name = route['gateway_id']
            # Try to resolve as internet gateway first
            gateway_id = get_aws_resource_id(gateway_name, 'internet_gateway', region)
            if gateway_id:
                resolved_route['gateway_id'] = gateway_id
            else:
                # Could try other gateway types here (nat_gateway, etc.)
                pass
        resolved_routes.append(resolved_route)

    return resolved_routes


# Legacy function aliases for backwards compatibility
def get_subnet_id_by_name(subnet_name, region='us-east-1'):
    """Legacy wrapper - use get_aws_resource_id instead."""
    return get_aws_resource_id(subnet_name, 'subnet', region)


def get_subnet_ids_by_names(subnet_names, region='us-east-1'):
    """Legacy wrapper - use get_aws_resource_ids instead."""
    return get_aws_resource_ids(subnet_names, 'subnet', region)


class FilterModule:
    """Ansible filter plugin for AWS operations."""

    def filters(self):
        return {
            # New generic filters
            'get_aws_resource_id': get_aws_resource_id,
            'get_aws_resource_ids': get_aws_resource_ids,
            'resolve_route_gateway_ids': resolve_route_gateway_ids,
            # Legacy filters for backwards compatibility
            'get_subnet_id_by_name': get_subnet_id_by_name,
            'get_subnet_ids_by_names': get_subnet_ids_by_names,
        }
