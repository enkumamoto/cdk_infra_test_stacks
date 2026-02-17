from aws_cdk import aws_ec2 as ec2, aws_iam as iam

def create_bastion(stack, vpc, puppet_bucket, vpn_sg):
    """Cria SG, role e instância do Bastion. Adiciona regra de ingresso para VPN."""
    # Bastion SG
    bastion_sg = ec2.SecurityGroup(
        stack,
        "BastionSG",
        vpc=vpc,
        description="SG for Bastion Hosts",
        allow_all_outbound=True,
    )
    
    bastion_sg.add_ingress_rule(
        peer=vpn_sg,
        connection=ec2.Port.tcp(22),
        description="Allow VPN access to Bastion via SSH",
    )
    
    # Bastion Role
    bastion_role = iam.Role(
        stack,
        "BastionRole",
        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
    )
    
    bastion_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonSSMManagedInstanceCore"
        )
    )
    
    # Bastion Host
    ami = ec2.MachineImage.latest_amazon_linux2023()
    
    bastion_host = ec2.Instance(
        stack,
        "BastionHost",
        vpc=vpc,
        vpc_subnets=ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        instance_type=ec2.InstanceType("t3.micro"),
        machine_image=ami,
        security_group=bastion_sg,
        role=bastion_role,
    )
    
    puppet_bucket.grant_read(bastion_host.role)
    
    bastion_host.add_user_data(
        "yum install -y amazon-ssm-agent",
        "systemctl enable amazon-ssm-agent",
        "systemctl start amazon-ssm-agent",
        "yum install -y puppet",
        "cd /home/ec2-user",
        f"aws s3 sync s3://{puppet_bucket.bucket_name}/puppet /opt/puppet",
        "puppet apply puppet/manifests/site.pp"
    )
    
    return bastion_host