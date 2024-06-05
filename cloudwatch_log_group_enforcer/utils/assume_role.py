import boto3

def assume_role(role_arn):
    sts_client = boto3.client("sts")
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="log-group-enforcer"
    )
    return assumed_role_object["Credentials"]
