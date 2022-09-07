#!/usr/bin/env python3

""" Entry point for starting the CDK App """

from aws_cdk import core
from cicd_pr_stack import CICDPullRequestStack
from cdk_nag import AwsSolutionsChecks
import cdk_nag

app = core.App()
stack = CICDPullRequestStack(app, "CICDPullRequestStack")

cdk_nag.NagSuppressions.add_stack_suppressions(
    stack,
    [
        cdk_nag.NagPackSuppression(
            id="AwsSolutions-L1",
            reason="Already using latest version 3.9 for lambda",
        )
    ],
)


cdk_nag.NagSuppressions.add_stack_suppressions(
    stack,
    [
        cdk_nag.NagPackSuppression(
            id="AwsSolutions-IAM4",
            reason="Use AWS managed poclicies AWSLambdaBasicExecutionRole",
        )
    ],
)

cdk_nag.NagSuppressions.add_stack_suppressions(
    stack,
    [
        cdk_nag.NagPackSuppression(
            id="AwsSolutions-IAM5",
            reason="Use AWS managed poclicies CodeBuild Project with defaults from cdk",
        )
    ],
)

cdk_nag.NagSuppressions.add_stack_suppressions(
    stack,
    [
        cdk_nag.NagPackSuppression(
            id="AwsSolutions-CB4",
            reason="Use Defaults from CodeBuild Project with defaults from cdk.",
        )
    ],
)

core.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
