import aws_cdk as core
import aws_cdk.assertions as assertions

from cache_cluster.cache_cluster_stack import CacheClusterStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cache_cluster/cache_cluster_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CacheClusterStack(app, "cache-cluster")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
