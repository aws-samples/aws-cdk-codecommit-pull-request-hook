'''
The AWS cdk stack looks for the available AWS CodeCommit repository in the AWS_DEFAULT_REGION 
and then applies a AWS Code Build trigger using the spec buildspec-tests.json.
'''
from typing import Dict
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_codecommit as _code,
    aws_codebuild as codebuild,
    aws_events as events,
    aws_events_targets as targets,
)

import boto3

code_client = boto3.client("codecommit")

import json
class CICDPullRequestStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_publish_build_result = _lambda.Function(
            self,
            "PullRequestPublishCodeBuildResult",
            function_name="PullRequestAutomation",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("lambda_publish_build_result"),
            handler="handler.lambda_handler",
        )

        # pass these additional info to build trigger events which would be later available
        # as environment variable for lamda fucntion which is invoked at build state changes
        # this is needed to put comment on PR request
        input_transformer = events.RuleTargetInput.from_object(
            {
                "sourceIdentifier": events.EventField.from_path(
                    "$.detail.repositoryNames[0]"
                ),
                "sourceVersion": events.EventField.from_path("$.detail.sourceCommit"),
                "artifactsOverride": {"type": "NO_ARTIFACTS"},
                "environmentVariablesOverride": [
                    {
                        "name": "PULL_REQUEST_ID",
                        "value": events.EventField.from_path("$.detail.pullRequestId"),
                        "type": "PLAINTEXT",
                    },
                    {
                        "name": "REPOSITORY_NAME",
                        "value": events.EventField.from_path(
                            "$.detail.repositoryNames[0]"
                        ),
                        "type": "PLAINTEXT",
                    },
                    {
                        "name": "SOURCE_COMMIT",
                        "value": events.EventField.from_path("$.detail.sourceCommit"),
                        "type": "PLAINTEXT",
                    },
                    {
                        "name": "DESTINATION_COMMIT",
                        "value": events.EventField.from_path(
                            "$.detail.destinationCommit"
                        ),
                        "type": "PLAINTEXT",
                    },
                    {
                        "name": "REVISION_ID",
                        "value": events.EventField.from_path("$.detail.revisionId"),
                        "type": "PLAINTEXT",
                    },
                ],
            }
        )

        response = code_client.list_repositories()
        my_repos = [item["repositoryName"] for item in response["repositories"]]
        if not my_repos:
            print("No repo found, please make sure if you are using correct AWS regsion. e.g export AWS_DEFAULT_REGION=eu-west-2; when codecommit repository exist in eu-west-2.")
            return

        for my_repo in my_repos:
            my_repository = _code.Repository.from_repository_name(
                self, f"{my_repo}_Repository", repository_name=my_repo
            )
            # grant permissions to put comments on Pull request.
            my_repository.grant(lambda_publish_build_result, "codecommit:P*Comment*")

            project = codebuild.Project(
                self,
                f"{my_repo}_PullRequestTestAutomationProject",
                build_spec=codebuild.BuildSpec.from_source_filename("buildspec-tests.yaml"),
                source=codebuild.Source.code_commit(repository=my_repository),
                environment= {
                    "build_image": codebuild.LinuxBuildImage.AMAZON_LINUX_2_3
                }
            )

            pull_request_rule = events.Rule(
                self,
                f"{my_repo}_PullRequestNotification",
                event_pattern=events.EventPattern(
                    source=["aws.codecommit"],
                    resources=[my_repository.repository_arn],
                    detail={
                        "event": [
                            "pullRequestCreated",
                            "pullRequestSourceBranchUpdated",
                        ]
                    },
                ),
            )

            pull_request_rule.add_target(
                target=targets.CodeBuildProject(project, event=input_transformer)
            )

            project.on_state_change(
                f"{my_repo}_PullRequestBuildStateChange",
                target=targets.LambdaFunction(lambda_publish_build_result),
            )
