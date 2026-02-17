from aws_cdk import RemovalPolicy, aws_ecr as ecr

def create_ecr(stack):
    """Cria o repositório ECR."""
    ecr_repo = ecr.Repository(
        stack,
        "AppRepository",
        removal_policy=RemovalPolicy.DESTROY,
        image_scan_on_push=True,
    )
    return ecr_repo