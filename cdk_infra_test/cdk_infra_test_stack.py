from aws_cdk import Stack
from constructs import Construct
from .vpc import create_vpc
from .s3 import create_s3_bucket
from .vpn import create_vpn_and_certificates
from .bastion import create_bastion
from .rds import create_rds
from .ecr import create_ecr
from .ecs import create_ecs
from .alb import create_alb
from .outputs import create_outputs

class CdkInfraTestStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Criar VPC primeiro (dependência para outros)
        self.vpc = create_vpc(self)
        
        # Criar S3 Bucket
        self.puppet_bucket = create_s3_bucket(self)
        
        # Criar VPN e certificados (CA, certificados, VPN endpoint, etc.) - retorna client_vpn e vpn_sg
        client_vpn, vpn_sg = create_vpn_and_certificates(self, self.vpc)
        
        # Criar Bastion (depende de VPC, S3 e VPN SG)
        self.bastion_host = create_bastion(self, self.vpc, self.puppet_bucket, vpn_sg)
        
        # Criar RDS (depende de VPC)
        self.db_cluster = create_rds(self, self.vpc)
        
        # Criar ECR
        self.ecr_repo = create_ecr(self)
        
        # Criar ECS (depende de VPC, DB, ECR) - retorna ecs_cluster, ecs_sg e service
        self.ecs_cluster, ecs_sg, service = create_ecs(self, self.vpc, self.db_cluster, self.ecr_repo)
        
        # Criar ALB (depende de VPC e ECS service)
        alb = create_alb(self, self.vpc, service)
        
        # Criar Outputs (depende de todos os recursos)
        create_outputs(self, alb, self.bastion_host, self.db_cluster, self.puppet_bucket, client_vpn)