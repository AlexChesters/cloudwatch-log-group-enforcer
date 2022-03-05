import os
import sys

if 'LAMBDA_TASK_ROOT' in os.environ:
  sys.path.append(f"{os.environ['LAMBDA_TASK_ROOT']}/package")

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import boto3


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

    print(len(log_groups))
