import os
import sys

if 'LAMBDA_TASK_ROOT' in os.environ:
  sys.path.append(f"{os.environ['LAMBDA_TASK_ROOT']}/package")

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import boto3


client = boto3.client("logs", region_name="eu-west-1")
log_groups = []


def fetch_log_groups(nextToken=None):
    if nextToken:
        response = client.describe_log_groups(nextToken=nextToken)
    else:
        response = client.describe_log_groups()

    for group in response["logGroups"]:
        log_groups.append(group)

    if "nextToken" in response:
        print("next token found")
        fetch_log_groups(response["nextToken"])
    else:
        return


def handler(event, context):
    fetch_log_groups()
    print("found {0} log groups".format(len(log_groups)))
