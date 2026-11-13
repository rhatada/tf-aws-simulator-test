from behave import given, when, then
from botocore.exceptions import ClientError


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("AWS Emulator が起動している")
def step_emulator_running(context):
    try:
        context.ec2.describe_vpcs(MaxResults=5)
    except Exception as e:
        raise AssertionError(f"AWS Emulator に接続できません: {e}")


@given('Terraform で "{project}" プロジェクトのリソースが適用済みである')
def step_terraform_applied(context, project):
    context.project = project


# ---------------------------------------------------------------------------
# When — VPC
# ---------------------------------------------------------------------------

@when('VPC タグ "Name" が "{name}" のリソースを取得する')
def step_get_vpc_by_name(context, name):
    resp = context.ec2.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [name]}]
    )
    vpcs = resp.get("Vpcs", [])
    context.vpc = vpcs[0] if vpcs else None


# ---------------------------------------------------------------------------
# Then — VPC
# ---------------------------------------------------------------------------

@then("VPC が存在する")
def step_vpc_exists(context):
    assert context.vpc is not None, "VPC が見つかりません"


@then('VPC の CIDR は "{cidr}" である')
def step_vpc_cidr(context, cidr):
    assert context.vpc["CidrBlock"] == cidr, (
        f"期待 CIDR: {cidr}, 実際: {context.vpc['CidrBlock']}"
    )


@then("VPC の DNS ホスト名が有効になっている")
def step_vpc_dns_hostnames(context):
    vpc_id = context.vpc["VpcId"]
    resp = context.ec2.describe_vpc_attribute(VpcId=vpc_id, Attribute="enableDnsHostnames")
    enabled = resp["EnableDnsHostnames"]["Value"]
    assert enabled, "DNS ホスト名が無効です"


@then("VPC の DNS 解決が有効になっている")
def step_vpc_dns_support(context):
    vpc_id = context.vpc["VpcId"]
    resp = context.ec2.describe_vpc_attribute(VpcId=vpc_id, Attribute="enableDnsSupport")
    enabled = resp["EnableDnsSupport"]["Value"]
    assert enabled, "DNS 解決が無効です"


# ---------------------------------------------------------------------------
# Then — サブネット
# ---------------------------------------------------------------------------

@then("その VPC にサブネットが {count:d} つ存在する")
def step_subnet_count(context, count):
    vpc_id = context.vpc["VpcId"]
    resp = context.ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    context.subnets = resp.get("Subnets", [])
    assert len(context.subnets) >= count, (
        f"サブネット数が不足: 期待 {count}, 実際 {len(context.subnets)}"
    )


@then('サブネット "{name}" の CIDR は "{cidr}" である')
def step_subnet_cidr(context, name, cidr):
    matched = [
        s for s in context.subnets
        if any(t["Key"] == "Name" and t["Value"] == name for t in s.get("Tags", []))
    ]
    assert matched, f'サブネット "{name}" が見つかりません'
    assert matched[0]["CidrBlock"] == cidr, (
        f'サブネット "{name}" の CIDR: 期待 {cidr}, 実際 {matched[0]["CidrBlock"]}'
    )


# ---------------------------------------------------------------------------
# When / Then — セキュリティグループ
# ---------------------------------------------------------------------------

@when('セキュリティグループ名 "{name}" を取得する')
def step_get_sg(context, name):
    resp = context.ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [name]}]
    )
    sgs = resp.get("SecurityGroups", [])
    context.security_group = sgs[0] if sgs else None


@then("セキュリティグループが存在する")
def step_sg_exists(context):
    assert context.security_group is not None, "セキュリティグループが見つかりません"


@then("インバウンドルールにポート {port:d} (TCP) が設定されている")
def step_sg_inbound_port(context, port):
    rules = context.security_group.get("IpPermissions", [])
    matched = [
        r for r in rules
        if r.get("IpProtocol") == "tcp"
        and r.get("FromPort") == port
        and r.get("ToPort") == port
    ]
    assert matched, f"ポート {port}/TCP のインバウンドルールが見つかりません"
    context.matched_rule = matched[0]


@then('インバウンドの送信元 CIDR は "{cidr}" である')
def step_sg_inbound_cidr(context, cidr):
    cidrs = [r["CidrIp"] for r in context.matched_rule.get("IpRanges", [])]
    assert cidr in cidrs, f"送信元 CIDR {cidr} が見つかりません (実際: {cidrs})"


# ---------------------------------------------------------------------------
# When / Then — DB サブネットグループ
# ---------------------------------------------------------------------------

@when('DB サブネットグループ名 "{name}" を取得する')
def step_get_db_subnet_group(context, name):
    try:
        resp = context.rds.describe_db_subnet_groups(DBSubnetGroupName=name)
        groups = resp.get("DBSubnetGroups", [])
        context.db_subnet_group = groups[0] if groups else None
    except ClientError:
        context.db_subnet_group = None


@then("DB サブネットグループが存在する")
def step_db_subnet_group_exists(context):
    assert context.db_subnet_group is not None, "DB サブネットグループが見つかりません"


@then("DB サブネットグループに {count:d} つ以上のサブネットが含まれる")
def step_db_subnet_group_count(context, count):
    subnets = context.db_subnet_group.get("Subnets", [])
    assert len(subnets) >= count, (
        f"サブネット数が不足: 期待 {count}+, 実際 {len(subnets)}"
    )


# ---------------------------------------------------------------------------
# When / Then — DB パラメータグループ
# ---------------------------------------------------------------------------

@when('DB パラメータグループ名 "{name}" を取得する')
def step_get_db_parameter_group(context, name):
    try:
        resp = context.rds.describe_db_parameter_groups(DBParameterGroupName=name)
        groups = resp.get("DBParameterGroups", [])
        context.db_parameter_group = groups[0] if groups else None
    except ClientError:
        context.db_parameter_group = None


@then("DB パラメータグループが存在する")
def step_db_parameter_group_exists(context):
    assert context.db_parameter_group is not None, "DB パラメータグループが見つかりません"


@then('DB パラメータグループのファミリーは "{family}" である')
def step_db_parameter_group_family(context, family):
    actual = context.db_parameter_group.get("DBParameterGroupFamily")
    assert actual == family, f"ファミリー: 期待 {family}, 実際 {actual}"


@then('パラメータ "{name}" の値は "{value}" である')
def step_db_parameter_value(context, name, value):
    group_name = context.db_parameter_group["DBParameterGroupName"]
    resp = context.rds.describe_db_parameters(DBParameterGroupName=group_name)
    params = {p["ParameterName"]: p.get("ParameterValue") for p in resp.get("Parameters", [])}
    assert name in params, f'パラメータ "{name}" が見つかりません'
    assert params[name] == value, (
        f'パラメータ "{name}": 期待 {value}, 実際 {params[name]}'
    )


# ---------------------------------------------------------------------------
# When / Then — RDS インスタンス
# ---------------------------------------------------------------------------

@when('RDS インスタンス識別子 "{identifier}" を取得する')
def step_get_rds_instance(context, identifier):
    try:
        resp = context.rds.describe_db_instances(DBInstanceIdentifier=identifier)
        instances = resp.get("DBInstances", [])
        context.db_instance = instances[0] if instances else None
    except ClientError:
        context.db_instance = None


@then("RDS インスタンスが存在する")
def step_rds_instance_exists(context):
    assert context.db_instance is not None, "RDS インスタンスが見つかりません"


@then('RDS のエンジンは "{engine}" である')
def step_rds_engine(context, engine):
    actual = context.db_instance.get("Engine")
    assert actual == engine, f"エンジン: 期待 {engine}, 実際 {actual}"


@then('RDS のインスタンスクラスは "{cls}" である')
def step_rds_instance_class(context, cls):
    actual = context.db_instance.get("DBInstanceClass")
    assert actual == cls, f"インスタンスクラス: 期待 {cls}, 実際 {actual}"


@then('RDS のストレージタイプは "{storage_type}" である')
def step_rds_storage_type(context, storage_type):
    actual = context.db_instance.get("StorageType")
    assert actual == storage_type, f"ストレージタイプ: 期待 {storage_type}, 実際 {actual}"


@then("RDS のストレージ暗号化が有効になっている")
def step_rds_encrypted(context):
    assert context.db_instance.get("StorageEncrypted"), "ストレージ暗号化が無効です"


@then("RDS のマルチ AZ は無効である")
def step_rds_multi_az(context):
    assert not context.db_instance.get("MultiAZ"), "マルチ AZ が有効になっています"


@then("RDS のパブリックアクセスは無効である")
def step_rds_public(context):
    assert not context.db_instance.get("PubliclyAccessible"), "パブリックアクセスが有効です"


@then("RDS のバックアップ保持期間は {days:d} 日間である")
def step_rds_backup(context, days):
    actual = context.db_instance.get("BackupRetentionPeriod")
    assert actual == days, f"バックアップ保持期間: 期待 {days}, 実際 {actual}"


@then('RDS のデータベース名は "{name}" である')
def step_rds_db_name(context, name):
    actual = context.db_instance.get("DBName")
    assert actual == name, f"データベース名: 期待 {name}, 実際 {actual}"


@then('RDS のマスターユーザー名は "{username}" である')
def step_rds_username(context, username):
    actual = context.db_instance.get("MasterUsername")
    assert actual == username, f"マスターユーザー名: 期待 {username}, 実際 {actual}"


@then('RDS の DB サブネットグループは "{name}" である')
def step_rds_subnet_group(context, name):
    actual = context.db_instance.get("DBSubnetGroup", {}).get("DBSubnetGroupName")
    assert actual == name, f"DB サブネットグループ: 期待 {name}, 実際 {actual}"


@then('RDS の DB パラメータグループは "{name}" である')
def step_rds_parameter_group(context, name):
    groups = context.db_instance.get("DBParameterGroups", [])
    names = [g["DBParameterGroupName"] for g in groups]
    assert name in names, f"DB パラメータグループ {name} が見つかりません (実際: {names})"
