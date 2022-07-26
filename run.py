import importlib

main = importlib.import_module('cloudwatch_log_group_enforcer.main')

main.handler({}, {})
