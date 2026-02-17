from aws_cdk import RemovalPolicy, aws_s3 as s3

def create_s3_bucket(stack):
    """Cria o bucket S3 para Puppet."""
    puppet_bucket = s3.Bucket(
        stack,
        "PuppetBucket",
        bucket_name="puppet-bucket",
        versioned=True,
        removal_policy=RemovalPolicy.DESTROY,
        auto_delete_objects=True,
        encryption=s3.BucketEncryption.S3_MANAGED,
        block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
    )
    return puppet_bucket