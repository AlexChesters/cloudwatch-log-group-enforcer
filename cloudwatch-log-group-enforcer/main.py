import os
import sys

if 'LAMBDA_TASK_ROOT' in os.environ:
  sys.path.append(f"{os.environ['LAMBDA_TASK_ROOT']}/package")

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import boto3

DEFAULT_RETENTION = 3

client = boto3.client("logs", region_name="eu-west-1")
paginator = client.get_paginator("describe_log_groups")


def flatten(l):
    return [item for sublist in l for item in sublist]


def handler(event, context):
    results = [
        result["logGroups"]
        for result in paginator.paginate()
    ]

    log_groups = flatten(results)

    for log_group in log_groups:
        if "retentionInDays" not in log_group:
            print(
                "log group {0} does not have retention, enforcing one of {1} days"
                .format(log_group["logGroupName"], DEFAULT_RETENTION)
            )
            client.put_retention_policy(
                logGroupName=log_group["logGroupName"],
                retentionInDays=DEFAULT_RETENTION
            )
