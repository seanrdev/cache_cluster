from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
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
        vpc = ec2.Vpc(self, "VPC")
        sg_ec2 = ec2.SecurityGroup(
            self,
            id="ec2-sample-secgroup",
            vpc=vpc,
            security_group_name="ec2-sample-secgroup"
        )
        subnet_group2 = elcache.CfnSubnetGroup(
            self,
            'MySubnetGroup',
            #vpc=vpc,
            description='My rds Sub',
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
            security_group=sg_ec2,
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

        # cache.t4g.micro
        memcache = elcache.CfnCacheCluster(
            self,
            "ElastiCacheGroup",
            cache_node_type="cache.t4g.micro",
            engine="memcached",
            cache_subnet_group_name=subnet_group2.cache_subnet_group_name,
            num_cache_nodes=4,
            az_mode="cross-az",
            cluster_name="SampleCluster",
            engine_version="1.6.6",
            port=43334,
            vpc_security_group_ids=[sg_ec2.security_group_id],
        )

        memcache.add_depends_on(subnet_group2)
