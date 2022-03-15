""" Lambda function that adds a comment to the Pull Request with the tests results """

import boto3
import json

codecommit_client = boto3.client("codecommit")


def lambda_handler(event, context):
    """Lambda handler function"""
    print("request: {}".format(json.dumps(event)))

    for item in event["detail"]["additional-information"]["environment"][
        "environment-variables"
    ]:
        if item["name"] == "PULL_REQUEST_ID":
            pull_request_id = item["value"]
        if item["name"] == "REPOSITORY_NAME":
            repository_name = item["value"]
        if item["name"] == "SOURCE_COMMIT":
            before_commit_id = item["value"]
        if item["name"] == "DESTINATION_COMMIT":
            after_commit_id = item["value"]

    build_status = event["detail"]["build-status"]
    logs_path = event["detail"]["additional-information"]["logs"]["deep-link"]
    s3_prefix = (
        "s3-{0}".format(event["region"]) if event["region"] != "us-east-1" else "s3"
    )

    if build_status == "IN_PROGRESS":
        start_time = event["detail"]["additional-information"]["build-start-time"]
        content = f"** on pull request build started at {start_time} **"

    elif build_status == "FAILED":
        failed_badge = f'https://{s3_prefix}.amazonaws.com/codefactory-{event["region"]}-prod-default-build-badges/failing.svg'
        content = f'![Failing]({failed_badge} "Failing") - See the [Logs]({logs_path})'

    elif build_status == "SUCCEEDED":
        pass_badge = f'https://{s3_prefix}.amazonaws.com/codefactory-{event["region"]}-prod-default-build-badges/passing.svg'
        content = f'![Passing]({pass_badge} "Passing") - See the [Logs]({logs_path})'

    elif build_status == "STOPPED":
        content = f"STOPPED - See the [Logs]({logs_path})"
    else:
        return

    codecommit_client.post_comment_for_pull_request(
        pullRequestId=pull_request_id,
        repositoryName=repository_name,
        beforeCommitId=before_commit_id,
        afterCommitId=after_commit_id,
        content=content,
    )
    print(content)
