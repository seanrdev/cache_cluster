from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elb,
    aws_elasticache as elcache,
)

from constructs import Construct


class CacheClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        userdata = ec2.UserData.for_linux(shebang="#!/bin/bash")
        userdata.add_commands(
            "yum update -y",
            "yum install -y httpd",
            "systemctl start httpd",
            "systemctl enable httpd",
            "echo \"<h1>Hello World from $(hostname -f)</h1>\" >> /var/www/html/index.html",
        )
        vpc = ec2.Vpc(
            self,
            "VPC",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Public-Subnet',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name='Private-Subnet',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=23,
                )
            ]
        )
        security_group_memcache = ec2.SecurityGroup(
            self,
            id="memcache_security_group",
            vpc=vpc,
            security_group_name="memcache-security-group"
        )

        security_group_instances = ec2.SecurityGroup(
            self,
            id="ec2_instance_group",
            vpc=vpc,
            security_group_name="ec2-instance-group"
        )

        subnet_group = elcache.CfnSubnetGroup(
            self,
            'MySubnetGroup',
            description='My Memcached Sub',
            cache_subnet_group_name="sample-subnet-group",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets]
        )

        asg = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            # user_data=some_defined_data_not_defined_yet
            user_data=userdata,
            security_group=security_group_instances,
            min_capacity=2,
            max_capacity=4,
        )

        lb = elb.ApplicationLoadBalancer(
            self,
            "lb",
            vpc=vpc,
            internet_facing=True,
        )

        listener = lb.add_listener(
            "Listener",
            port=80,
            open=True,
        )

        listener.add_targets(
            "ApplicationCluster",
            port=80,
            targets=[asg],
        )

        # Security group for memcached
        security_group_memcache.connections.allow_from(
            security_group_instances, ec2.Port.tcp(43334),
        )
        # Security group for instances / Load balancer / autoscaling group
        security_group_instances.connections.allow_from(
            security_group_memcache, ec2.Port.tcp(43334),
        )
        # cache.t4g.micro
        memcached0 = elcache.CfnCacheCluster(
            self,
            "Cache0",
            cache_node_type="cache.t4g.micro",
            engine="memcached",
            cache_subnet_group_name=subnet_group.cache_subnet_group_name,
            num_cache_nodes=4,
            az_mode="cross-az",
            preferred_availability_zones=["us-east-1a", "us-east-1b", "us-east-1a", "us-east-1b"],
            cluster_name="Cluster0",
            engine_version="1.6.6",
            port=43334,
            vpc_security_group_ids=[security_group_memcache.security_group_id],
        )

        memcached1 = elcache.CfnCacheCluster(
            self,
            "Cache1",
            cache_node_type="cache.t4g.micro",
            engine="memcached",
            cache_subnet_group_name=subnet_group.cache_subnet_group_name,
            num_cache_nodes=4,
            az_mode="cross-az",
            preferred_availability_zones=["us-east-1a", "us-east-1b", "us-east-1a", "us-east-1b"],
            cluster_name="Cluster1",
            engine_version="1.6.6",
            port=43334,
            vpc_security_group_ids=[security_group_memcache.security_group_id],
        )

        memcached2 = elcache.CfnCacheCluster(
            self,
            "Cache2",
            cache_node_type="cache.t4g.micro",
            engine="memcached",
            cache_subnet_group_name=subnet_group.cache_subnet_group_name,
            num_cache_nodes=4,
            az_mode="cross-az",
            preferred_availability_zones=["us-east-1a", "us-east-1b", "us-east-1a", "us-east-1b"],
            cluster_name="Cluster2",
            engine_version="1.6.6",
            port=43334,
            vpc_security_group_ids=[security_group_memcache.security_group_id],
        )

        memcached3 = elcache.CfnCacheCluster(
            self,
            "Cache3",
            cache_node_type="cache.t4g.micro",
            engine="memcached",
            cache_subnet_group_name=subnet_group.cache_subnet_group_name,
            num_cache_nodes=4,
            az_mode="cross-az",
            preferred_availability_zones=["us-east-1a", "us-east-1b", "us-east-1a", "us-east-1b"],
            cluster_name="Cluster3",
            engine_version="1.6.6",
            port=43334,
            vpc_security_group_ids=[security_group_memcache.security_group_id],
        )
        memcached0.add_depends_on(subnet_group)
        memcached1.add_depends_on(subnet_group)
        memcached2.add_depends_on(subnet_group)
        memcached3.add_depends_on(subnet_group)
