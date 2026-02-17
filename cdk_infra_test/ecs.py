from aws_cdk import aws_ec2 as ec2, aws_iam as iam, aws_ecs as ecs

def create_ecs(stack, vpc, db_cluster, ecr_repo):
    """Cria cluster ECS, SG, task definition e service. Retorna ecs_cluster, ecs_sg e service."""
    # ECS Cluster
    ecs_cluster = ecs.Cluster(
        stack,
        "AppCluster",
        vpc=vpc,
    )
    
    # ECS Security Group
    ecs_sg = ec2.SecurityGroup(
        stack,
        "EcsSG",
        vpc=vpc,
        description="SG for ECS",
        allow_all_outbound=True,
    )
    
    # Allow ECS to access DB
    db_cluster.connections.allow_from(
        ecs_sg,
        ec2.Port.tcp(5432),
        description="Allow ECS to access DB",
    )
    
    # Task Role
    task_role = iam.Role(
        stack,
        "EcsTaskRole",
        assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    )
    
    task_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonECSTaskExecutionRolePolicy"
        )
    )
    
    task_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(
            "SecretsManagerReadWrite"
        )
    )
    
    # Task Definition
    task_def = ecs.FargateTaskDefinition(
        stack,
        "AppTaskDef",
        memory_limit_mib=512,
        cpu=256,
        task_role=task_role,
    )
    
    # Container
    container = task_def.add_container(
        "FastAPIContainer",
        image=ecs.ContainerImage.from_ecr_repository(ecr_repo, tag="latest"),
        logging=ecs.LogDrivers.aws_logs(stream_prefix="fastapi"),
        environment={
            "DB_NAME": "appdb",
            "DB_HOST": db_cluster.cluster_endpoint.hostname,
        },
        secrets={
            "DB_USER": ecs.Secret.from_secrets_manager(
                db_cluster.secret,
                field="username",
            ),
            "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                db_cluster.secret,
                field="password",
            ),
        },        
    )
    
    container.add_port_mappings(
        ecs.PortMapping(
            container_port=8000,
            host_port=8000,
            protocol=ecs.Protocol.TCP,
        )
    )
    
    # ECS Service
    service = ecs.FargateService(
        stack,
        "AppService",
        cluster=ecs_cluster,
        task_definition=task_def,
        desired_count=1,
        assign_public_ip=False,
        security_groups=[ecs_sg],
        vpc_subnets=ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        ),
    )
    
    return ecs_cluster, ecs_sg, service