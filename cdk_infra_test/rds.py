from aws_cdk import RemovalPolicy, aws_ec2 as ec2, aws_rds as rds

def create_rds(stack, vpc):
    """Cria SG, subnet group e cluster RDS."""
    # RDS SG
    db_sg = ec2.SecurityGroup(
        stack,
        "DatabaseSG",
        vpc=vpc,
        description="SG for Database",
    )
    
    # Nota: Regras de ingresso serão adicionadas no ECS se necessário.
    
    # RDS Private Subnet
    db_subnet_group = rds.SubnetGroup (
        stack,
        "DataBaseSubnetGroup",
        description = "Database Subnet Group",
        vpc=vpc,
        vpc_subnets=ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        removal_policy=RemovalPolicy.DESTROY,
    
    )
    
    # RDS Cluster
    db_cluster = rds.DatabaseCluster(
        stack,
        "DatabaseCluster",
        engine=rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_14_6
            ),
        writer=rds.ClusterInstance.serverless_v2("writer"),
        readers=[
            rds.ClusterInstance.serverless_v2("reader")
            ],
        vpc=vpc,
        subnet_group=db_subnet_group,
        security_groups=[db_sg],
        credentials = rds.Credentials.from_generated_secret("postres"),
        default_database_name="appdb",
        serverless_v2_min_capacity = 0.5,
        serverless_v2_max_capacity = 1,
        removal_policy=RemovalPolicy.DESTROY,   
    )
    
    return db_cluster