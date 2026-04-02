# Copilot Instructions

## Purpose

`cloudwatch-log-group-enforcer` is an AWS Lambda function written in Python that enforces retention policies on CloudWatch Log Groups across multiple AWS accounts. Any log group without a retention policy is given a default retention of **3 days** (`DEFAULT_RETENTION` in `cloudwatch_log_group_enforcer/main.py`).

## Repository Structure

```
cloudwatch_log_group_enforcer/   # Main Python package (Lambda source code)
  __init__.py
  main.py                        # Lambda handler entry point
  accounts/
    get_accounts_to_inspect.py   # Discovers target AWS accounts via CloudFormation StackSet
  utils/
    assume_role.py               # STS AssumeRole helper
    flatten.py                   # List flattening helper
run.py                           # Local development entry point (calls main.handler directly)
stacks/
  accounts-janitor-account/
    infrastructure.yml           # SAM template: Lambda, IAM role, CloudWatch alarm
    parameters/infrastructure.json
  management-account/
    log-group-enforcer-role.yml  # IAM role deployed to the management account
    deploy.sh                    # Manual deploy script for the management-account stack
ci/
  codepipeline.yml               # AWS CodePipeline / CodeBuild CI/CD pipeline definition
scripts/
  pipeline.sh                    # Script to deploy the CodePipeline stack
buildspec.yml                    # CodeBuild build specification
package.sh                       # Packages the Lambda deployment artifact
Makefile                         # Developer convenience targets
pyproject.toml                   # uv project metadata and dependencies
uv.lock                          # Locked dependency versions
```

## Key Constants (`cloudwatch_log_group_enforcer/main.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `DEFAULT_RETENTION` | `3` | Days of retention applied to log groups that have none |
| `REGION_DENYLIST` | `["me-south-1", ...]` | Regions that are explicitly skipped before the availability check (e.g. regions that are unreachable due to infrastructure outages) |

When adding a region to the denylist, add a comment explaining why.

## Language and Dependencies

- **Python 3.9** (matches the Lambda runtime)
- **uv** for dependency management
- Runtime dependency: `boto3 ^1.25.4` (AWS SDK)
- No test framework is configured; there are currently **no automated tests**.

## Build and Run

### Install dependencies

```bash
uv install        # installs project dependencies into a virtual environment
```

Or run both in sequence via:

```bash
make build   # clean + package
```

### Package for Lambda deployment

```bash
make package   # runs package.sh, produces lambda_dist/lambda.zip
```

`package.sh` builds a wheel, pip-installs it into `lambda_dist/`, and zips that directory.

### Run locally

```bash
make run   # requires the "accounts-janitor" AWS CLI profile to be configured
```

This executes `run.py`, which calls `main.handler({}, {})` directly.

## Architecture and AWS Account Layout

The solution spans multiple AWS accounts:

| Account | Role | Account ID |
|---------|------|------------|
| `accounts-janitor` | Hosts the Lambda function | `723247229166` |
| Management account | Hosts the CloudFormation StackSet that records target accounts | `008356366354` |
| Target accounts | Accounts whose log groups are inspected and fixed | discovered dynamically |

### How it works (execution flow)

1. Lambda is triggered on a **daily schedule** (EventBridge `rate(1 day)`).
2. `get_accounts_to_inspect()` assumes `arn:aws:iam::008356366354:role/cloudwatch-log-group-enforcer-list-accounts` and calls `cloudformation:ListStackInstances` on the StackSet **`log-group-enforcer-role`** in `eu-west-1` to get the list of target account IDs.
3. For each target account, the Lambda assumes `arn:aws:iam::<account_id>:role/cloudwatch-log-group-enforcer-target-account-role`.
4. Regions in `REGION_DENYLIST` are filtered out before iteration. Remaining regions are then checked for availability via `sts.get_caller_identity()`; any region returning a `ClientError` is also skipped.
5. For each available AWS region, it pages through all CloudWatch Log Groups using `describe_log_groups`.
6. Any log group missing a `retentionInDays` value receives a `put_retention_policy` call setting it to `DEFAULT_RETENTION` (3 days).

## CloudFormation / SAM Templates

- **`stacks/accounts-janitor-account/infrastructure.yml`** — SAM template (requires `Transform: AWS::Serverless-2016-10-31`). Defines the Lambda execution role, the Lambda function, and a CloudWatch alarm on Lambda errors. The `CodeUri` points to `../../lambda_dist/` which is the output of `package.sh`.
- **`stacks/management-account/log-group-enforcer-role.yml`** — Plain CloudFormation. Creates the `cloudwatch-log-group-enforcer-list-accounts` IAM role in the management account, allowing the Lambda's role to assume it and call `cloudformation:ListStackInstances`.

## CI/CD Pipeline

Defined in `ci/codepipeline.yml` and deployed with `scripts/pipeline.sh`. The pipeline:

1. **Source** — clones the `main` branch from GitHub via a CodeStar connection.
2. **Build** — runs `make build` and then `aws cloudformation package` to upload the Lambda artifact to S3 and inline it into the SAM template.
3. **Deploy** — deploys the packaged SAM template as CloudFormation stack `live-cloudwatch-log-group-enforcer-infrastructure`.

The pipeline is deployed to the `accounts-janitor` AWS account in `eu-west-1`.

## Known Issues / Notes

- There are no unit or integration tests. When adding new logic, consider adding a `tests/` directory with `pytest`.
- The Lambda timeout is set to **600 seconds** (10 minutes) to allow for processing many accounts and regions.
