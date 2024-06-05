set -e

aws cloudformation deploy \
  --template-file log-group-enforcer-role.yml \
  --stack-name log-group-enforcer-role \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-1 \
  --profile management
