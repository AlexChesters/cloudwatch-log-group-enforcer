import importlib

main = importlib.import_module('cloudwatch-log-group-enforcer.main')

main.handler({}, {})
