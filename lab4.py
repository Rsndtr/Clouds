import boto3
from botocore.exceptions import ClientError


def create_key_pair(key_name):
    ec2_client = boto3.client("ec2", region_name="us-west-2")

    # Check if the key pair already exists
    response = ec2_client.describe_key_pairs()
    for key_pair in response["KeyPairs"]:
        if key_pair["KeyName"] == key_name:
            print(f"The key pair {key_name} already exists")
            return

    # Create the key pair if it doesn't already exist
    key_pair = ec2_client.create_key_pair(KeyName=key_name)
    private_key = key_pair["KeyMaterial"]
    with open(f"{key_name}.pem", "w+") as handle:
        handle.write(private_key)
    print(f"The key pair {key_name} was created successfully")


def create_instance():
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    instances = ec2_client.run_instances(
        ImageId="ami-0b0154d3d8011b0cd",
        MinCount=1,
        MaxCount=1,
        InstanceType="t4g.nano",
        KeyName="ec2-key-pair")

    print(instances["Instances"][0]["InstanceId"])


def list_instances():
    client = boto3.resource('ec2', region_name="us-west-2")
    instances = client.instances.all()
    result = []
    for instance in instances:
        result.append((instance.id, instance.state['Name']))
    print(result)
    return result


def get_running_instances():
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        },
        {
            "Name": "instance-type",
            "Values": ["t4g.nano"]
        }
    ]).get("Reservations")
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
    print(f"{instance_id}, {instance_type}, {public_ip},{private_ip}")


def stop_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def start_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    response = ec2_client.start_instances(InstanceIds=[instance_id])
    print(response)


def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(response)


def create_bucket(bucket_name, region="us-west-2"):
    s3_client = boto3.client('s3', region_name=region)
    location = {'LocationConstraint': region}

    try:
        response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print("Bucket created successfully.")
    except s3_client.exceptions.BucketAlreadyExists as e:
        print(f"Error creating bucket: {e}")
    except s3_client.exceptions.BucketAlreadyOwnedByYou as e:
        print(f"Error creating bucket: {e}")


def list_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f' {bucket["Name"]}')


def upload_file_to_s3(file_path, bucket_name, object_name=None):
    s3_client = boto3.client('s3')

    if object_name is None:
        object_name = file_path

    try:
        response = s3_client.upload_file(file_path, bucket_name, object_name)
    except Exception as e:
        print(e)
        return False

    return True


def read_from_s3(bucket_name, object_key):
    s3 = boto3.resource('s3')

    # Check if the bucket exists
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket {bucket_name} does not exist.")
        else:
            print(f"An error occurred while checking the bucket: {e}")
        return

    # Check if the object key exists in the bucket
    bucket = s3.Bucket(bucket_name)
    objs = list(bucket.objects.filter(Prefix=object_key))
    if len(objs) == 0:
        print(f"No object found in {bucket_name} with key {object_key}.")
        return

    obj = bucket.Object(object_key)

    # Read the contents of the object
    try:
        response = obj.get()
        content = response['Body'].read().decode('utf-8')
        print(content)
    except ClientError as e:
        print(f"An error occurred while reading object {object_key}: {e}")


def delete_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # check if bucket exists
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        # bucket does not exist
        if e.response['Error']['Code'] == '404':
            print(f"Bucket {bucket_name} does not exist")
            return
        else:
            raise

    # delete all objects in the bucket
    bucket.objects.all().delete()

    # delete the bucket
    bucket.delete()

    print(f"Bucket {bucket_name} deleted successfully.")


def menu():

    while True:
        option = input("0-Create key pair \n1-Create EC2 instance \n2-List running instances "
                       "\n3-Start instance \n4-Stop instance\n5-Delete EC2 instance"
                       "\n6-Create S3 bucket\n7-List buckets\n8-Upload to s3\n9-Read from s3"
                       "\n10-Delete S3 bucket\n11-List instances\n12-exit\nChoose an option:")

        if option == "1":
            create_instance()
        elif option == "2":
            get_running_instances()
        elif option == "3":
            ins_id = input("Enter the instance ID: ")
            start_instance(ins_id)
        elif option == "4":
            ins_id = input("Enter the instance ID: ")
            stop_instance(ins_id)
        elif option == "5":
            ins_id = input("Enter the instance ID: ")
            terminate_instance(ins_id)
        elif option == "6":
            bucket_name = input("Enter the name for your S3 bucket: ")
            create_bucket(bucket_name)
        elif option == "7":
            list_buckets()
        elif option == "8":
            file_path = input("file_path: ")
            bucket_name = input("bucket_name: ")
            object_name = input("object_name: ")
            upload_file_to_s3(file_path, bucket_name, object_name)
        elif option == "9":
            bucket_name = input("bucket_name: ")
            object_key = input("object_name: ")
            read_from_s3(bucket_name, object_key)
        elif option == "10":
            bucket_name = input("bucket_name: ")
            delete_bucket(bucket_name)
        elif option == "11":
            list_instances()
        elif option == "12":
            exit()
        elif option == "0":
            create_key_pair(input("key_name: "))



menu()
