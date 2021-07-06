#!/usr/bin/env python3

from aws_cdk import core
from cicd_pr_stack import CICDPullRequestStack 

app = core.App()
CICDPullRequestStack(app, "CICDPullRequestStack")

app.synth()
