import copy
import yaml
import requests


class LintRules(object):

    def __init__(self):
        self.__aws_rules = {}
        self.__custom_rules = {}
        self.__cloudformation_rules = {}

        self.initialize()

    def initialize(self, custom_rules_path=None):
        self._load_aws_rules()

        self.__cloudformation_rules = copy.deepcopy(self.__aws_rules)

        if custom_rules_path:
            self._load_custom_rules(custom_rules_path)
            self._merge_rules()

    def _merge_rules(self):
        aws_resources = self.__aws_rules["ResourceTypes"]
        custom_resources = self.__custom_rules["Resources"]
        cloudformation_resources = self.__cloudformation_rules["ResourceTypes"]

        # Cannot manipulate a dictionary while looping through it, so
        # Use the original AWS rules for this.
        for aws_resource, aws_properties in aws_resources.items():

            # Remove unsupported resources
            if aws_resource not in custom_resources:
                del cloudformation_resources[aws_resource]
                continue

        for cfn_resource, cfn_properties in cloudformation_resources.items():

            # Update mandatory properties
            custom_resource = custom_resources[cfn_resource]
            if not custom_resource:
                continue

            custom_properties = custom_resource["Properties"]
            if not custom_properties:
                continue

            for custom_property, property_values in custom_properties.items():

                cfn_property = cfn_properties["Properties"][custom_property]

                # Override mandatory properties
                cfn_property["Required"] = True

                # Add allowed values property
                if property_values:
                    cfn_property['AllowedValues'] = property_values['Values']

    def _load_aws_rules(self):
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-resource-specification.html
        json_request = requests.get('https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json')  # noqa: E501
        self.__aws_rules = json_request.json()

    def _load_custom_rules(self, custom_rules_path):
        yaml_file = open(custom_rules_path)
        self.__custom_rules = yaml.load(yaml_file)

    @property
    def cloudformation_rules(self):
        return self.__cloudformation_rules
