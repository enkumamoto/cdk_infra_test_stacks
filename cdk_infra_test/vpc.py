from aws_cdk import aws_ec2 as ec2

def create_vpc(stack):
    """Cria a VPC com sub-redes públicas e privadas."""
    vpc = ec2.Vpc(
        stack,
        "VPCDevOpsTest",
        max_azs=2,
        nat_gateways=1,
        subnet_configuration=[
            ec2.SubnetConfiguration(
                name="public",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=24,
            ),
            ec2.SubnetConfiguration(
                name="private",
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=24,
            ),
        ],
    )
    return vpc