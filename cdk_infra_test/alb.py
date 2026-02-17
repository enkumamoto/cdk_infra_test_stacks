from aws_cdk import Duration, aws_elasticloadbalancingv2 as elbv2

def create_alb(stack, vpc, service):
    """Cria ALB e listener, conectando ao ECS service."""
    # ALB
    alb = elbv2.ApplicationLoadBalancer(
        stack,
        "AppALB",
        vpc=vpc,
        internet_facing=True,
    )

    listener = alb.add_listener(
        "HttpListener",
        port=80,
        open=True,
    )

    listener.add_targets(
        "EcsTargets",
        port=80,
        targets=[service],
        health_check=elbv2.HealthCheck(
            path="/health",
            interval=Duration.seconds(30),
        ),
    )
    
    return alb