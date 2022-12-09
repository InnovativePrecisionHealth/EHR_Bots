import json
import boto3
import base64
from botocore.exceptions import ClientError

 
def get_secret(secret_name:str, region_name:str):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
     )
            
    except ClientError as e:
        print(f"Error: {e}")
        if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                print(e)
                raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                print(e)
                raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                print(e)
                raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                print(e)
                raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                print(e)
                raise e

    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
        else:
                decoded_binary_secret = base64.b64decode(
                    get_secret_value_response['SecretBinary'])
                return decoded_binary_secret





def get_secret_piedmont():
    secret = json.loads(get_secret("piedmont_EHR_login", "us-east-2"))
    print(secret)
    return secret

def get_secret_INI():
    secret = json.loads(get_secret("INI_EHR_login", "us-east-2"))
    print(secret)
    return secret

def get_secret_frontier():
    secret = json.loads(get_secret("frontier_EHR_login", "us-east-2"))
    print(secret)
    return secret

def get_secret_burst():
    secret = json.loads(get_secret("burstAuth", "us-east-2"))
    print(secret)
    return secret

def get_secret_TIND():
    secret = json.loads(get_secret("TIND_EHR_login", "us-east-2"))
    print(secret)
    return secret