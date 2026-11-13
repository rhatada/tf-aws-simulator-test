import os
import ssl
import boto3
import urllib3

EMULATOR_ENDPOINT = os.environ.get("AWS_ENDPOINT_URL", "https://127.0.0.1:9297")
CA_BUNDLE = os.environ.get("AWS_CA_BUNDLE", os.path.expanduser("~/.aws/emulator/9297/ca.pem"))
REGION = os.environ.get("AWS_DEFAULT_REGION", "ap-northeast-1")
ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "test")
SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")


def _make_client(service: str):
    return boto3.client(
        service,
        region_name=REGION,
        endpoint_url=EMULATOR_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        verify=CA_BUNDLE,
    )


def before_all(context):
    context.ec2 = _make_client("ec2")
    context.rds = _make_client("rds")


def before_scenario(context, scenario):
    context.vpc = None
    context.subnets = []
    context.security_group = None
    context.db_subnet_group = None
    context.db_parameter_group = None
    context.db_instance = None
