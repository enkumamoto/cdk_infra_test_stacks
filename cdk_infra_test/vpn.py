from aws_cdk import aws_ec2 as ec2, aws_acmpca as acmpca, aws_certificatemanager as acm

def create_vpn_and_certificates(stack, vpc):
    """Cria CA, certificados e VPN Client. Retorna client_vpn e vpn_sg."""
    # CA
    vpn_ca = acmpca.CfnCertificateAuthority(
        stack,
        "VpnPrivateCA",
        type="ROOT",
        key_algorithm="RSA_2048",
        signing_algorithm="SHA384withRSA",
        subject=acmpca.CfnCertificateAuthority.SubjectProperty(
            country="BR",
            organization="DevOpsTest",
            organizational_unit="IT",
            common_name="vpn.devops.local",
        ),
    )

    # Certificado da própria CA (self-signed)
    ca_certificate = acmpca.CfnCertificate(
        stack,
        "VpnPrivateCACertificate",
        certificate_authority_arn=vpn_ca.attr_arn,
        certificate_signing_request=vpn_ca.attr_certificate_signing_request,
        signing_algorithm="SHA384withRSA",
        template_arn="arn:aws:acm-pca:::template/RootCACertificate/V1",
        validity=acmpca.CfnCertificate.ValidityProperty(
            type="YEARS",
            value=10,
        ),
    )

    # Ativação da CA
    acmpca.CfnCertificateAuthorityActivation(
        stack,
        "VpnPrivateCAActivation",
        certificate_authority_arn=vpn_ca.attr_arn,
        certificate=ca_certificate.attr_certificate,
        status="ACTIVE",
    )

    # Certificates
    server_cert = acm.Certificate(
        stack,
        "VpnServerCert",
        domain_name="vpn-server.devopstest.local",
    )
    
    client_cert = acm.Certificate(
        stack,
        "VpnClientCert",
        domain_name="vpn-client.devopstest.local",
    )
    
    # VPN Sg
    vpn_sg = ec2.SecurityGroup(
        stack,
        "VpnSG",
        vpc=vpc,
        description="SG for VPN Connections",
        allow_all_outbound=True,
    )
    
    # VPN Client
    client_vpn = ec2.CfnClientVpnEndpoint(
        stack,
        "ClientVpnEndpoint",
        authentication_options=[
            ec2.CfnClientVpnEndpoint.ClientAuthenticationRequestProperty(
                type="certificate-authentication",
                mutual_authentication=ec2.CfnClientVpnEndpoint.CertificateAuthenticationRequestProperty(
                    client_root_certificate_chain_arn=client_cert.certificate_arn,
                ),
            ),
        ],
        client_cidr_block="10.100.0.0/22",
        connection_log_options=ec2.CfnClientVpnEndpoint.ConnectionLogOptionsProperty(
            enabled=False,
        ),
        server_certificate_arn=server_cert.certificate_arn,
        vpc_id=vpc.vpc_id,
        security_group_ids=[vpn_sg.security_group_id],
        split_tunnel=True,
        transport_protocol="udp",
    )
    
    # Private Subnet VPN Association
    ec2.CfnClientVpnTargetNetworkAssociation(
        stack,
        "VpnAssociation",
        client_vpn_endpoint_id=client_vpn.ref,
        subnet_id=vpc.private_subnets[0].subnet_id,
    )
    
    # VPN Access Auth
    ec2.CfnClientVpnAuthorizationRule(
        stack,
        "VpnAuthRule",
        client_vpn_endpoint_id=client_vpn.ref,
        target_network_cidr=vpc.vpc_cidr_block,
        authorize_all_groups=True,
    )
    
    return client_vpn, vpn_sg