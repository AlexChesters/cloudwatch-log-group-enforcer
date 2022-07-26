import os
import sys

if 'LAMBDA_TASK_ROOT' in os.environ:
  sys.path.append(f"{os.environ['LAMBDA_TASK_ROOT']}/package")

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import boto3
from boto3.session import Session
from botocore.exceptions import ClientError


DEFAULT_RETENTION = 3


def flatten(l):
    return [item for sublist in l for item in sublist]


def region_is_available(region):
    sts = boto3.client('sts', region_name=region)
    try:
        sts.get_caller_identity()
        return True
    except ClientError:
        return False


def handler(_event, _context):
    session = Session()
    regions = session.get_available_regions("cloudwatch")

    for region in regions:
        if not region_is_available(region):
            print(f"region {region} is not enabled, skipping it")
            continue

        client = boto3.client("logs", region_name=region)
        paginator = client.get_paginator("describe_log_groups")

        results = [
            result["logGroups"]
            for result in paginator.paginate()
        ]

        log_groups = flatten(results)

        for log_group in log_groups:
            if "retentionInDays" not in log_group:
                log_group_name = log_group["logGroupName"]
                print(
                    f"log group {log_group_name} (region: {region}) does not have retention, enforcing one of {DEFAULT_RETENTION} days"
                )
                client.put_retention_policy(
                    logGroupName=log_group["logGroupName"],
                    retentionInDays=DEFAULT_RETENTION
                )
