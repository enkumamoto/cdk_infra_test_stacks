from aws_cdk import CfnOutput

def create_outputs(stack, alb, bastion_host, db_cluster, puppet_bucket, client_vpn):
    """Cria os CfnOutputs para a stack."""
    CfnOutput(
        stack,
        "ApplicationURL",
        value=f"http://{alb.load_balancer_dns_name}",
        description="Public URL of the FastAPI application",
    )

    CfnOutput(
        stack,
        "BastionInstanceID",
        value=bastion_host.instance_id,
        description="Bastion Instance ID",
    )
    
    CfnOutput(
        stack,
        "DatabaseClusterEndpoint",
        value=db_cluster.cluster_endpoint.hostname,
        description="Database Cluster Endpoint",
    )
    
    CfnOutput(
        stack,
        "DatabaseName",
        value="appdb",
        description="Database name"
    )
    
    CfnOutput(
        stack,
        "DatabaseSecretArn",
        value=db_cluster.secret.secret_arn,
        description="Secret ARN for database credentials"
    )
    
    CfnOutput(
        stack, 
        "PuppetBucketName", 
        value=puppet_bucket.bucket_name
    )
    
    CfnOutput(
        stack,
        "VpnEndpointId",
        value=client_vpn.ref,
        description="Client VPN Endpoint ID",
    )