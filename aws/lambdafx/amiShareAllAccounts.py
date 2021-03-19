import json
import boto3
import os
import botocore
from botocore.exceptions import ClientError


MASTER_ACCOUNT_ID = '936232839634'
REGION = 'us-east-1'

#create session for aws creds
def get_session(region, access_id, secret_key):
    return boto3.session.Session(region_name='us-east-1',
            aws_access_key_id=access_id,
            aws_secret_access_key=secret_key)

# Function to convert list to string
def Convert(account_id):
    li = list(account_id.split(","))
    return li

def lambda_handler(event, context):

    #Create session using your current creds
    boto_sts = boto3.client('sts')

    #Request to assume the role like this, the ARN is the Role's ARN from
    #the other account you wish to assume. Not your current ARN.
    stsresponse = boto_sts.assume_role(
        RoleArn='arn:aws:iam::'+MASTER_ACCOUNT_ID+':role/NCICBIITOrgAccessRole',
        RoleSessionName="newSession"
    )

    #Save the details from assumed role into vars
    newsession_id = stsresponse["Credentials"]["AccessKeyId"]
    newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
    newsession_token = stsresponse["Credentials"]["SessionToken"]

    #Create Organizations client with the assumed creds
    organization_client = boto3.client('organizations', region_name=REGION,
        aws_access_key_id = newsession_id,
        aws_secret_access_key = newsession_key,
        aws_session_token = newsession_token
    )

    #create role session creds to be assumed
    session = get_session(os.getenv('REGION'),
                          os.getenv('ACCESS_KEY_ID'),
                          os.getenv('SECRET_KEY'))

    #create ec2 client with assumed creds
    ec2_client = session.client('ec2')

    #create System Manager client with the assumed creds
    ssm_client = session.client('ssm')

    #get parameters value from system manager
    centos_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/centos', WithDecryption=False)
    centos_docker_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/centosdocker', WithDecryption=False)
    rhel7_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/rhel7', WithDecryption=False)
    win2k12_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/win2k12', WithDecryption=False)
    win2k12AH_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/win2k12-AH', WithDecryption=False)
    win2k16_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/win2k16', WithDecryption=False)
    win2k16AH_ssm_parameter = ssm_client.get_parameter(Name='/ami/latest/us-east-1/win2k16-AH', WithDecryption=False)

    #get all all accounts within AWS Organizations
    #keeps getting accounts while NextToken is not null
    org_response = organization_client.list_accounts()
    accounts = []
    while org_response:
        accounts += org_response['Accounts']
        org_response = organization_client.list_accounts(NextToken=org_response['NextToken']) if 'NextToken' in org_response else None

    #for all AWS accounts prints AWS Account #
    #set the system manager parameter to the AMI ID
    #adds the launch Permission for all AWS Accounts ID
    for account_id in accounts:
            print(account_id['Id'])

            if account_id['Id'] is None:
                break

            ec2_client.modify_image_attribute(
                ImageId=centos_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
            ec2_client.modify_image_attribute(
                ImageId=centos_docker_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
            ec2_client.modify_image_attribute(
                ImageId=rhel7_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
            ec2_client.modify_image_attribute(
                ImageId=win2k12_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
            ec2_client.modify_image_attribute(
                ImageId=win2k12AH_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
            ec2_client.modify_image_attribute(
                ImageId=win2k16_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
            ec2_client.modify_image_attribute(
                ImageId=win2k16AH_ssm_parameter['Parameter']['Value'],
                Attribute='launchPermission',
                OperationType='add',
                UserIds = Convert(account_id['Id'])
            )
