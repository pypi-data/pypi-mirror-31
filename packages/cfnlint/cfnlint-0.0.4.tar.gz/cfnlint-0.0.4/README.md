# cfnlinter

The `cfnlint` package is an AWS CloudFormation linter that uses the [AWS CloudFormation Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) and is customizable and extendible with a custom ruleset.

Package is available through [`pip`](https://pypi.org/project/cfnlint/):

```
pip install cfnlint
```

## Current features

* Lint specified Cloudformation yaml file
* Lint agains `eu-west-1` [CloudFormation definition](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html)

## Upcoming features

* Tests, linter, Code Conventions, etc.
* Add Custom rules to extend/override the AWS specification
* Lint against specific region
* Add Pluggable system to add custom resource handlers for special/extended rules

### Roadmap

Current planned roadmap:

Version | Functionality
--------|--------------
0.1.x   | Initialize release with basic functionality (yaml only). Customisation: <ul><li>Allowed resources</li><li>Override `required` properties</li><li>Enumerators (Allowed values)</li><li>Top-level property support only</li></ul>
0.2.x   | Add json support. Customisation:<ul><li>Additional documentation URL</li><li>Regular Expression support</li><li>Sub-properties support</li></ul>
0.3.x   | ?



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
