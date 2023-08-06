# Configuring an AWS account for this package

## Create Cloudformation Stack

To Create the cloudformation stack (first time only):

 export REGION=<region, e.g. us-east-2>
 aws cloudformation --region ${REGION} create-stack --stack-name iotdevices-iam-base  --capabilities CAPABILITY_IAM --template-body file://cloudformation/create_iam_groups_and_policies.yml

If you need to update the stack:

 export REGION=<region, e.g. us-east-2>
 aws cloudformation --region ${REGION} update-stack --stack-name iotdevices-iam-base  --capabilities CAPABILITY_IAM --template-body file://cloudformation/create_iam_groups_and_policies.yml

## First time configuring a region in an account

this only needs to be performed once:

```python
    import boto3.session
    from iotdeviceprovisioner import configure_account_region

    region = "us-east-2"  # change this as appropriate
    boto3_session = boto3.session.Session(region_name=region)

    configure_account_region(boto3_session)
```



## Provisioning a device

This will generate

```python
    import boto3.session
    from iotdeviceprovisioner import provision_device

    region = "us-east-2"  # change as appropriate
    boto3_session = boto3.session.Session(region_name=region)
    provision_device("devicename", "beta",
                     boto3_session=boto3_session)

```


## Rotating Credentials

This is the same workflow as provisioning a device.
