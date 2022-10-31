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

    organisations_client = boto3.client("organizations")
    organisation_accounts_paginator = organisations_client.get_paginator("list_accounts")

    organisation_accounts_results = [
        result["Accounts"]
        for result in organisation_accounts_paginator.paginate()
    ]

    organisation_accounts = flatten(organisation_accounts_results)

    management_account_id = "008356366354"

    for account in organisation_accounts:
        account_id = str(account["Id"])
        account_name = account["Name"]

        print(f"processing account {account_name} ({account_id})")

        credentials = None

        if account_id is not management_account_id:
            print(f"{account_name} is not the organisation management account, assuming role in target account")

            sts_client = boto3.client("sts")
            assumed_role_object = sts_client.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/cloudwatch-log-group-enforcer",
                RoleSessionName="log-group-enforcer"
            )
            credentials = assumed_role_object["Credentials"]

        for region in regions:
            if not region_is_available(region):
                print(f"region {region} is not enabled, skipping it")
                continue

            if credentials:
                logs_client = boto3.client(
                    "logs",
                    region_name=region,
                    aws_access_key_id=credentials["AccessKeyId"],
                    aws_secret_access_key=credentials["SecretAccessKey"],
                    aws_session_token=credentials["SessionToken"]
                )
            else:
                logs_client = boto3.client(
                    "logs",
                    region_name=region
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
