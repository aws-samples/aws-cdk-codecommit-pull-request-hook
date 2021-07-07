# AWS CDK for Building Pull Request Hook on AWS CodeCommit
### Table of contents
1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Project structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Tools and services](#tools-and-services)
6. [Usage](#usage)
7. [Clean up](#clean-up)

## Introduction
This project provides an example of building Pull Request Hook on AWS CodeCommit. 
It builds the necessary infrastructure to integrate automatic triggering of a AWS CodeBuild project when a Pull Request is raised in AWS CodeCommit and then links back the results (e.g. tests results) to the Pull Request.

## Architecture
![architecture](doc/architecture.png)

1. The creation of an [AWS CodeCommit](https://aws.amazon.com/codecommit/) Pull Request generates an event within [AWS EventBridge Events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-events.html), 
2. We are filtering for events which result in Pull Request creation or modification. 
3. This event json body has all the information relevant to the Pull Request which are required by the AWS Lambda function to add automated comments in Pull Request. 
The [environmentVariablesOverride](https://docs.aws.amazon.com/codebuild/latest/APIReference/API_StartBuild.html#CodeBuild-StartBuild-request-environmentVariablesOverride) feature of [AWS CodeBuild](https://aws.amazon.com/codebuild/) is then leveraged to start the AWS CodeBuild project execution.
4. Once the CodeBuild project run completes, this generates another event that is caught by a create Rule and invokes an AWS Lambda function.
 5. The function will add a comment to the Pull Request with the build outcomes (whether it passed or failed).
## Project structure
* [`cicd_pr_stack`](cicd_pr_stack.py) - defines the required [AWS CDK Stack](https://docs.aws.amazon.com/cdk/latest/guide/stacks.html).
* [`lambda_publish_build_result/handler.py`](lambda_publish_build_result/handler.py) - code of the [AWS Lambda](https://aws.amazon.com/lambda/) function that is triggered on build state change and publishes comments on the Pull request.
* [`buildspec-tests.yaml`](buildspec-tests.yaml) sample buildspec file used by the [AWS CodeBuild](https://aws.amazon.com/codebuild/) project. It provides an example of running plylint and pytest on the source code, modify it as per your use-case. Thiis specfile needs to be part of the repository as it's referred to by the AWS CodeBuild project.
* [`doc`](doc) - directory containing architecture diagrams.
* [`requirements.txt`](requirements.txt) - contains the python dependencies.

## Prerequisites
* [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html), installed
* [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) version 2, installed
* [Python 3](https://www.python.org/downloads/), installed

## Tools and services
* [AWS CDK](https://aws.amazon.com/cdk/) – The AWS Cloud Development Kit (AWS CDK) is a software development framework for defining your cloud infrastructure and resources by using programming languages such as TypeScript, JavaScript, Python, Java, and C#/.Net.
* [AWS Lambda](https://aws.amazon.com/lambda/) -  AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers, creating workload-aware cluster scaling logic, maintaining event integrations, or managing runtimes.
* [AWS CodeBuild](https://aws.amazon.com/codebuild/) - AWS CodeBuild is a fully managed continuous integration service that compiles source code, runs tests, and produces software packages that are ready to deploy.
* [AWS CodeCommit](https://aws.amazon.com/codecommit/) - AWS CodeCommit is a secure, highly scalable, managed source control service that hosts private Git repositories.

* [AWS EventBridge Events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-events.html) - Amazon EventBridge is a serverless event bus service that you can use to connect your applications with data from a variety of sources

## Usage 
Set the region where your AWS CodeCommit repository is provisioned.
e.g
```
export AWS_DEFAULT_REGION=eu-central-1
```

then follow the instructions on [Running CDK Python Examples](https://github.com/aws-samples/aws-cdk-examples/tree/master/python#running-examples) to deploy your stack.

## Clean up
Follow [AWS CDK instructions](https://docs.aws.amazon.com/cdk/latest/guide/hello_world.html#hello_world_tutorial_destroy) to remove AWS CDK stack from your account.

## Reference
This solution is inspired by this original [AWS DevOps Blog](https://aws.amazon.com/blogs/devops/validating-aws-codecommit-pull-requests-with-aws-codebuild-and-aws-lambda/)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.