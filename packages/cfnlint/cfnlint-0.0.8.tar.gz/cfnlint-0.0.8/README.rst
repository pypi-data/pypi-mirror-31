cfnlint - Extended AWS CloudFormation linter
============================================

The `cfnlint` package is an AWS CloudFormation linter that uses the [AWS CloudFormation Resource Specification](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html) and is customizable and extendible with a custom ruleset.

A custom ruleset is optional and adds the following features:

* Specify supported Resources: Block the specification of specific Resources
* Override required Properties: Make non-required properties required to enforce the specification of Properties
* Enumerators: Specify a list of allowed values to enforce Property values to a set of 1 or more values.

Pre-Alpha
---------
Current version is work in progress and only supported a minimal set of features:

* Current version only support `yaml` CloudFormation files
* Commandline support available (`cfn-lint --help`)
