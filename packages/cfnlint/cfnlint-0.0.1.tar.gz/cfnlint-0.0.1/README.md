# cfnlinter
AWS Cloudformation linter

## Current features

* Lint specified Cloudformation yaml file
* Lint agains `eu-west-1` [CloudFormation definition](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html)

## Upcoming features

* Tests, linter, Code Conventions, etc.
* Add Custom rules to extend/override the AWS specification
* Lint against specific region
* Add Pluggable system to add custom resource handlers for special/extended rules


### Setup Virtual Environment
Optional but recommended. Example:

```
$ virtualenv -p python3 venv
$ source venv/bin/activate
```

## Install requirements for development

```
$ pip install -e .
```

## Test Application (CLI)

```
$ cfn-lint --cfn_file test_stack.yaml
```
