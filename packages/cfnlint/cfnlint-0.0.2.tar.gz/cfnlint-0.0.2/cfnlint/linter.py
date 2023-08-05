import re
import yaml

from collections import OrderedDict
from cfnlint.core.lintrules import LintRules
from cfnlint.core.linter import Linter

def linter(file_path):
    __setup_yaml_module()

    errors = __lint_file(file_path)

    return errors


def __lint_file(file_path, custom_ruleset=None):

    all_errors = []

    # Load ruleset
    lintrules = LintRules()
    lintrules.initialize(custom_ruleset)

    # Lint!
    linter = Linter(file_path, lintrules.cloudformation_rules)
    linter.lint()

    all_errors += linter.errors

    return all_errors


def __setup_yaml_module():
    # preserve order while loading the YAML file by using an OrderedDict instead of a Dict
    # http://stackoverflow.com/a/21048064/3034356
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    yaml.add_constructor(_mapping_tag, __yaml_override_constructor)

    # pyyaml has problems with the CloudFormation functions (such as !Sub)
    # we 'remove' these functions by overriding the constructor again for these functions
    # http://stackoverflow.com/questions/7224033/default-constructor-parameters-in-pyyaml
    yaml.add_constructor('!And', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Base64', __yaml_override_cloudformation_function)
    yaml.add_constructor('!GetAtt', __yaml_override_cloudformation_function)
    yaml.add_constructor('!GetAZs', __yaml_override_cloudformation_function)
    yaml.add_constructor('!FindInMap', __yaml_override_cloudformation_function)
    yaml.add_constructor('!If', __yaml_override_cloudformation_function)
    yaml.add_constructor('!ImportValue', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Join', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Equals', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Ref', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Select', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Split', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Sub', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Not', __yaml_override_cloudformation_function)
    yaml.add_constructor('!Or', __yaml_override_cloudformation_function)


def __yaml_override_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


def __yaml_override_cloudformation_function(loader, node):
    return_value = node.tag + ' '

    if isinstance(node.value, str):
        # If a Cloudformation function is used, the result can be empty. Placeholder variables with "value"
        return_value += re.sub('\${[A-Za-z]*}', 'value', node.value)

    else:
        # convert lists to a meaningful representation of it was about
        return_value += '[' + ', '.join(str(item.value) for item in node.value) + ']'

    return return_value
