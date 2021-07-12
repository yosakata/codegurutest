#----------------
# my_functions.py
#-----------------
import boto3
import boto3
import datetime 
import os
from botocore.exceptions import ClientError
import time
import logging


def logging_setup(logfile):
  logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=logfile, level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  return logger

def log(Service, Name):
  print(f'{datetime.datetime.now(tz=datetime.timezone.utc)}\t{Service}\t{Name}')

def setup_vpc(VPC_NAME='myvpc', VPC_CIDR='10.0.0.0/16'):
  ec2 = boto3.resource('ec2')
  client = boto3.client('ec2')
  response = client.describe_vpcs(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ VPC_NAME ]
      }
    ]
  )
  if response['Vpcs']:
    vpc = ec2.Vpc(response['Vpcs'][0]['VpcId'])
    log('VPC already exists', VPC_NAME)
  else:
    vpc = ec2.create_vpc(
      CidrBlock=VPC_CIDR,
      TagSpecifications=[
        {
          'ResourceType': 'vpc',
          'Tags':[
            {
              "Key": "Name",
              "Value": VPC_NAME
            },
          ]
        }
      ]
    )
    log('VPC created', VPC_NAME)
  return vpc

def setup_internet_gateways(IGW_NAME, vpc):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  response = client.describe_internet_gateways(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ IGW_NAME ]
      }
    ]
  )
  if response['InternetGateways']:
    internet_gateway = ec2.InternetGateway(response['InternetGateways'][0]['InternetGatewayId'])
    log('Internet Gateway already exits', IGW_NAME)
  else:
    internet_gateway = ec2.create_internet_gateway(
      TagSpecifications=[
        {
          'ResourceType': 'internet-gateway',
          'Tags':[
            {
              "Key": "Name",
              "Value": IGW_NAME
            },
          ]
        }
      ]
    )
    vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)
    log('Internet Gateway created', IGW_NAME)
  return internet_gateway

def setup_route_table(RT_NAME, vpc, GatewayId):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  response = client.describe_route_tables(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ RT_NAME ]
      }
    ]
  )
  if response['RouteTables']:
    route_table = ec2.RouteTable(response['RouteTables'][0]['RouteTableId'])
    log('Route Table already exists', RT_NAME)
  else:
    route_table = vpc.create_route_table(
      TagSpecifications=[
        {
          'ResourceType': 'route-table',
          'Tags':[
            {
              "Key": "Name",
              "Value": RT_NAME
            },
          ]
        }
      ]
    )
    route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=GatewayId)
    log('Route Table created', RT_NAME)
  return route_table

def setup_instance(AMI, subnet_id, security_group_id, INSTANCE_NAME, key_pair_name, userdata, bool_public):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  response = client.describe_instances(
    Filters=[
      {
        'Name' : 'tag:Name',
        'Values' : [ INSTANCE_NAME ]
      },
      {
        'Name' : 'instance-state-name',
        'Values' : [ 'running', 'pending']
      }
    ]
  )
  if response['Reservations']:
    instance = ec2.Instance(response['Reservations'][0]['Instances'][0]['InstanceId'])
    log('EC2 Instance already exists', INSTANCE_NAME)
  else:
    instances = ec2.create_instances(
      BlockDeviceMappings=[
        {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 30,
                'VolumeType': 'gp3',
                'Encrypted': True
            },
        },
      ],
      ImageId=AMI,
      InstanceType='m5.large',
      EbsOptimized=True,
      MaxCount=1,
      MinCount=1,
      NetworkInterfaces=[
        {
          'SubnetId': subnet_id,
          'DeviceIndex': 0,
          'AssociatePublicIpAddress': bool_public,
          'Groups': [security_group_id],
          'PrivateIpAddress': '10.21.2.31'
          }
      ],
      KeyName=key_pair_name,
      UserData=userdata,
      TagSpecifications=[
        {
          'ResourceType': 'instance',
          'Tags':[
            {
              "Key": "Name",
              "Value": INSTANCE_NAME
            },
            {
              "Key": "auto-delete",
              "Value": "no"
            }
          ]
        }
      ]
    )
    instance = instances[0]
    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(
      InstanceIds=[instance.id]
    )
    log('EC2 Instance created', INSTANCE_NAME)
  return instance
 
def setup_subnet(SUBNET_NAME, SUBNET_CIDR, AZ, vpc, route_table):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')

  # check if subnet already exists.
  response = client.describe_subnets(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ SUBNET_NAME ]
      }
    ]
  )
  if response['Subnets']:
    subnet = ec2.Subnet(response['Subnets'][0]['SubnetId'])
    log('Subnet already exists', SUBNET_NAME)
  else:
    subnet = ec2.create_subnet(
      CidrBlock=SUBNET_CIDR, 
      VpcId=vpc.id,
      AvailabilityZone=AZ,
      TagSpecifications=[
        {
          'ResourceType': 'subnet',
          'Tags':[
            {
              "Key": "Name",
              "Value": SUBNET_NAME
            },
          ]
        }
      ]
    )
  route_table.associate_with_subnet(SubnetId=subnet.id)
  log('Subnet', SUBNET_NAME)
  return subnet

def setup_security_group(SG_NAME, vpc_id):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')

  response = client.describe_security_groups(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ SG_NAME ]
      }
    ]
  )
  if response['SecurityGroups']:
    security_group = ec2.SecurityGroup(response['SecurityGroups'][0]['GroupId'])
  else:
    security_group = ec2.create_security_group(
      GroupName=SG_NAME, 
      Description='----', 
      VpcId=vpc_id,
      TagSpecifications=[
        {
          'ResourceType': 'security-group',
          'Tags':[
            {
              "Key": "Name",
              "Value": SG_NAME
            },
          ]
        }
      ] 
    )      
    security_group.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
    security_group.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=80, ToPort=80)
  log('Security Group', SG_NAME)
  return security_group

def is_key_pair_exists(KEY_PAIR_NAME):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  # create a file to store the key locally
  response = client.describe_key_pairs(
    Filters=[
      {
        'Name' : "key-name",
        "Values" : [ KEY_PAIR_NAME ]
      }
    ]
  )
  if response(['KeyPairs']) == 0:
    return False
  else:
    return True

def create_key_pair(KEY_PAIR_NAME):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  key_pair_file = KEY_PAIR_NAME + ".pem"
  if os.path.exists(key_pair_file):
    os.remove(key_pair_file)
  outfile = open(key_pair_file, 'w')
  # create a key pair
  key_pair = ec2.create_key_pair(
    KeyName=KEY_PAIR_NAME,
    TagSpecifications=[
      {
        'ResourceType': 'key-pair',
        'Tags':[
          {
            "Key": "Name",
            "Value": KEY_PAIR_NAME
          },
        ]
      }
    ] 
  )
  # capture the key and store it in a file
  outfile.write(str(key_pair.key_material))
  log('Key pair', KEY_PAIR_NAME)
  return True
  
def setup_key_pair(KEY_PAIR_NAME):
  if not is_key_pair_exists(KEY_PAIR_NAME):
    create_key_pair(KEY_PAIR_NAME)

def setup_eip(EIP_NAME):
  client = boto3.client('ec2')
  response = client.describe_addresses(
      Filters=[
          {
              'Name': 'tag:Name',
              'Values': [EIP_NAME] 
          },
      ]
  )
  if response['Addresses']:
    AllocationId = response['Addresses'][0]['AllocationId']
  else:
    eip = client.allocate_address(
      Domain='vpc',
      TagSpecifications=[
        {
          'ResourceType': 'elastic-ip',
          'Tags':[
            {
              "Key": "Name",
              "Value": EIP_NAME
            },
          ]
        }
      ]
    )
    AllocationId = eip['AllocationId']
  log('Elastic IP', EIP_NAME)
  return AllocationId

def setup_nat_gateway(NGW_NAME, eip_id, subnet_id):
  client = boto3.client('ec2')
  response = client.describe_nat_gateways(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ NGW_NAME ]
      },
      {
        'Name' : "state",
        'Values' : ["available", "pending"]
      }
    ],
  )
  if response['NatGateways']:
    nat_gateway_id = response['NatGateways'][0]['NatGatewayId']
  else:
    nat_gateway = client.create_nat_gateway(
      AllocationId=eip_id,
      SubnetId = subnet_id,
      TagSpecifications=[
        {
          'ResourceType': 'natgateway',
          'Tags':[
            {
              "Key": "Name",
              "Value": NGW_NAME
            },
          ]
        }
      ]
    )
    nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']
    waiter = client.get_waiter('nat_gateway_available')
    waiter.wait(
      NatGatewayIds=[nat_gateway_id]
    )
  log('NAT Gateway', NGW_NAME)
  return nat_gateway_id

def delete_vpc(VPC_NAME):
  client = boto3.client('ec2')
  response = client.describe_vpcs(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ VPC_NAME ]
      }
    ]
  )
  if response['Vpcs']:
    client.delete_vpc(
      VpcId=response['Vpcs'][0]['VpcId']
    )
  log('VPC', VPC_NAME)

def delete_internet_gateway(IGW_NAME):
  client = boto3.client('ec2')
  response = client.describe_internet_gateways(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ IGW_NAME ]
      }
    ]
  )
  if response['InternetGateways']:
    if response['InternetGateways'][0]['Attachments']:
      internet_gateway_id = response['InternetGateways'][0]['InternetGatewayId']
      vpc_id = response['InternetGateways'][0]['Attachments'][0]['VpcId']

      client.detach_internet_gateway(
        InternetGatewayId=internet_gateway_id,
        VpcId=vpc_id
      )
    client.delete_internet_gateway(
      InternetGatewayId=internet_gateway_id
    )
  log("Internet Gateway", IGW_NAME)

def delete_route_table(RT_NAME):
  client = boto3.client('ec2')
  response = client.describe_route_tables(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ RT_NAME ]
      }
    ]
  )
  if response['RouteTables']:
    if response['RouteTables'][0]['Associations']:
      for i in range(len(response['RouteTables'][0]['Associations'])):
        client.disassociate_route_table(
          AssociationId=response['RouteTables'][0]['Associations'][i]['RouteTableAssociationId']
        )  
    client.delete_route_table(
      RouteTableId=response['RouteTables'][0]['RouteTableId']
    )
  log('Route Table', RT_NAME)

def delete_subnet(SUBNET_NAME):
  client = boto3.client('ec2')
  # check if subnet already exists.
  response = client.describe_subnets(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ SUBNET_NAME ]
      }
    ]
  )
  if response['Subnets']:
    client.delete_subnet(
      SubnetId=response['Subnets'][0]['SubnetId'])
  log('Subnet', SUBNET_NAME)

def delete_security_group(SG_NAME):
  client = boto3.client('ec2')
  response = client.describe_security_groups(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ SG_NAME ]
      }
    ]
  )
  if response['SecurityGroups']:
    client.delete_security_group(
      GroupId=response['SecurityGroups'][0]['GroupId']
    )
  log('Security Group', SG_NAME)

def delete_key_pair(KEY_PAIR_NAME):
  client = boto3.client('ec2')
  # create a file to store the key locally
  response = client.describe_key_pairs(
    Filters=[
      {
        'Name' : "key-name",
        "Values" : [ KEY_PAIR_NAME ]
      }
    ]
  )
  if response['KeyPairs']:
    client.delete_key_pair(
      KeyName=KEY_PAIR_NAME
    )
    if os.path.exists('{KEY_PAIR_NAME}.pem'):
      os.remove('{KEY_PAIR_NAME}.pem')
  log('Key Pair', KEY_PAIR_NAME)

def delete_instance(INSTANCE_NAME):
  client = boto3.client('ec2')
  response = client.describe_instances(
    Filters=[
      {
        'Name' : 'tag:Name',
        'Values' : [ INSTANCE_NAME ]
      },
      {
        'Name' : 'instance-state-name',
        'Values' : [ 'running', 'pending']
      }
    ]
  )
  if response['Reservations']:
    client.terminate_instances(
      InstanceIds=[response['Reservations'][0]['Instances'][0]['InstanceId']]
    )
    waiter = client.get_waiter('instance_terminated')
    waiter.wait(
      InstanceIds=[response['Reservations'][0]['Instances'][0]['InstanceId']]
    )
    log('EC2 Instance Deleted', INSTANCE_NAME)
  else:
    log('EC2 Instance Not Found', INSTANCE_NAME)

def delete_eip(EIP_NAME):
  client = boto3.client('ec2')
  response = client.describe_addresses(
      Filters=[
          {
              'Name': 'tag:Name',
              'Values': [EIP_NAME] 
          },
      ]
  )
  if response['Addresses']:
    client.release_address(
      AllocationId=response['Addresses'][0]['AllocationId']
    )
  log('Elastic IP', EIP_NAME)

def delete_nat_gateway(NGW_NAME):
  client = boto3.client('ec2')
  response = client.describe_nat_gateways(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ NGW_NAME ]
      },
      {
        'Name' : "state",
        'Values' : ["available", "pending"]
      }
    ],
  )
  if response['NatGateways']:
    client.delete_nat_gateway(
      NatGatewayId=response['NatGateways'][0]['NatGatewayId']
    )
    wait_deleted_nat_gateway(response['NatGateways'][0]['NatGatewayId'])
  log('Nat Gateway', NGW_NAME)

def wait_deleted_nat_gateway(NGW_ID):
  client = boto3.client('ec2')
  response = client.describe_nat_gateways(
    NatGatewayIds=[NGW_ID]
  )
  while True:
    if response['NatGateways'][0]['State'] == 'deleted':
      break
    time.sleep(5)
    response = client.describe_nat_gateways(
      NatGatewayIds=[NGW_ID]
    )

def delete_listener(LB_NAME):
  client = boto3.client('elbv2')
  load_balancer_arn = get_load_balancer_arn(LB_NAME)
  if load_balancer_arn == None:
    return 0
  else:
    listener_arn = get_listener_arn(load_balancer_arn)
    if load_balancer_arn == None:
      return 0
    else:
      response = client.delete_listener(
        ListenerArn=listener_arn
      )
  log('Listener', LB_NAME)

def delete_load_balancer(LB_NAME):
  client = boto3.client('elbv2')
  try:
    response = client.describe_load_balancers(
      Names=[LB_NAME]
    )
  except ClientError as e:
    pass
  else:
    client.delete_load_balancer(
      LoadBalancerArn=response['LoadBalancers'][0]['LoadBalancerArn']
    )
  log('Load Balancer', LB_NAME)

def delete_target_group(LB_TARGET_NAME):
  client = boto3.client('elbv2')
  try:
    response = client.describe_target_groups(
      Names=[ LB_TARGET_NAME ]
    )
  except ClientError as e:
    pass
  else:
    client.delete_target_group(
      TargetGroupArn=response['TargetGroups'][0]['TargetGroupArn']
    )
  log('Target Group', LB_TARGET_NAME)

def setup_load_balancer(LB_NAME, subnet_1_id, subnet_2_id, security_group_id):
  client = boto3.client('elbv2')
  try:
    response = client.describe_load_balancers(
      Names=[LB_NAME]
    )
  except ClientError as e:
    response = client.create_load_balancer(
      Name=LB_NAME,
      Subnets=[ 
        subnet_1_id, 
        subnet_2_id 
      ],
      SecurityGroups=[ security_group_id ]
    )
    load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    waiter = client.get_waiter('load_balancer_available')
    waiter.wait(
      LoadBalancerArns=[load_balancer_arn]
    )
  else:
    load_balancer_arn = get_load_balancer_arn(LB_NAME)
  log('Load Balancer', LB_NAME)
  return load_balancer_arn

def setup_target_group(LB_TARGET_NAME, vpc):
  client = boto3.client('elbv2')
  try:
    response = client.describe_target_groups(
      Names=[ LB_TARGET_NAME ]
    )
  except ClientError as e:
    response = client.create_target_group(
        Name=LB_TARGET_NAME,
        Port=80,
        Protocol='HTTP',
        VpcId=vpc.id,
    )
  log('Target Group', LB_TARGET_NAME)
  return response['TargetGroups'][0]['TargetGroupArn']

def register_targets(target_group_arn, instance_1_id, instance_2_id):
  client = boto3.client('elbv2')
  response = client.register_targets(
      TargetGroupArn=target_group_arn,
      Targets=[
          {
              'Id': instance_1_id,
              'Port': 80,
          },
          {
              'Id': instance_2_id,
              'Port': 80,
          },
      ],
  )

def setup_listener(target_group_arn, loadbalancer_arn):
  client = boto3.client('elbv2')
  response = client.create_listener(
      DefaultActions=[
          {
              'TargetGroupArn': target_group_arn,
              'Type': 'forward',
          },
      ],
      LoadBalancerArn=loadbalancer_arn,
      Port=80,
      Protocol='HTTP',
      Tags=[
        {
            'Key': 'Name',
            'Value': 'ELBHTTPListener'
        },
    ]
  )

# Get ID / ARN functions
def get_load_balancer_arn(LB_NAME):
  client = boto3.client('elbv2')
  try:
    response = client.describe_load_balancers(
      Names=[LB_NAME]
    )
  except ClientError as e:
    return None
  else:
    return response['LoadBalancers'][0]['LoadBalancerArn']

def get_vpc_id(VPC_NAME):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  response = client.describe_vpcs(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ VPC_NAME ]
      }
    ]
  )
  if response['Vpcs']:
    vpc = ec2.Vpc(response['Vpcs'][0]['VpcId'])
    return vpc.id
  else:
    return '0'

def get_vpc(VPC_NAME):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  response = client.describe_vpcs(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ VPC_NAME ]
      }
    ]
  )
  if response['Vpcs']:
    vpc = ec2.Vpc(response['Vpcs'][0]['VpcId'])
    return vpc
  else:
    return None

def get_subnet(SUBNET_NAME):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')
  # check if subnet already exists.
  response = client.describe_subnets(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ SUBNET_NAME ]
      }
    ]
  )
  if response['Subnets']:
    subnet = ec2.Subnet(response['Subnets'][0]['SubnetId'])
    return subnet
  else:
    return None

def get_security_group(SG_NAME):
  client = boto3.client('ec2')
  ec2 = boto3.resource('ec2')

  response = client.describe_security_groups(
    Filters=[
      {
        'Name' : "tag:Name",
        "Values" : [ SG_NAME ]
      }
    ]
  )
  if response['SecurityGroups']:
    security_group = ec2.SecurityGroup(response['SecurityGroups'][0]['GroupId'])
    return security_group
  else:
    return None

def get_target_group_arn(LB_TARGET_NAME):
  client = boto3.client('elbv2')
  response = client.describe_target_groups(
    Names=[LB_TARGET_NAME]
  )
  if response['TargetGroups']:
    return response['TargetGroups'][0]['TargetGroupArn']
  else:
    return '0'

def get_listener_arn(LB_ARN):
  client = boto3.client('elbv2')
  response = client.describe_listeners(
    LoadBalancerArn=LB_ARN
  )
  if response['Listeners']:
    return response['Listeners'][0]['ListenerArn']
  else:
    return None

