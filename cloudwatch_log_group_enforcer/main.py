import os
import sys

if 'LAMBDA_TASK_ROOT' in os.environ:
    sys.path.append(f"{os.environ['LAMBDA_TASK_ROOT']}/package")

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import boto3
from boto3.session import Session
from botocore.exceptions import ClientError

from cloudwatch_log_group_enforcer.accounts.get_accounts_to_inspect import get_accounts_to_inspect
from cloudwatch_log_group_enforcer.utils.assume_role import assume_role

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

    accounts_to_inspect = get_accounts_to_inspect()

    for account_id in accounts_to_inspect:
        print(f"processing account {account_id}")

        target_account_credentials = None

        for region in regions:
            if not region_is_available(region):
                print(f"region {region} is not enabled, skipping it")
                continue

            target_account_credentials = assume_role(f"arn:aws:iam::{account_id}:role/cloudwatch-log-group-enforcer-target-account-role")

            logs_client = boto3.client(
                "logs",
                region_name=region,
                aws_access_key_id=target_account_credentials["AccessKeyId"],
                aws_secret_access_key=target_account_credentials["SecretAccessKey"],
                aws_session_token=target_account_credentials["SessionToken"]
            )

            log_groups_paginator = logs_client.get_paginator("describe_log_groups")

            log_group_results = [
                result["logGroups"]
                for result in log_groups_paginator.paginate()
            ]

            log_groups = flatten(log_group_results)

            for log_group in log_groups:
                if "retentionInDays" not in log_group:
                    log_group_name = log_group["logGroupName"]
                    print(
                        f"log group {log_group_name} (region: {region}) does not have retention, enforcing one of {DEFAULT_RETENTION} days"
                    )
                    logs_client.put_retention_policy(
                        logGroupName=log_group["logGroupName"],
                        retentionInDays=DEFAULT_RETENTION
                    )
