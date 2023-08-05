from cfnlint.core.BaseYamlLinter import BaseYamlLinter


class Linter(BaseYamlLinter):

    def lint(self):
        resources = self.file_as_yaml['Resources']

        lintingrules = self.lintingrules['ResourceTypes']

        for resource_name, resource in resources.items():

            # Skip custom resources, cannot be linted
            if resource['Type'].startswith("Custom::"):
                continue

            # Check if the resource is supported
            if resource['Type'] not in lintingrules:

                self.errors.append(
                    "Unsupported resource: %s (%s)" % (resource_name, resource['Type'])
                )
                continue

            # Check if there are rules specified for the resource
            if not lintingrules[resource['Type']]:
                continue

            if not 'Properties' in resource:
                continue

            # Check mandatory properties
            resource_properties = resource['Properties']

            rule_properties = lintingrules[resource['Type']]['Properties']

            # If there are no required resources, skip
            if not rule_properties:
                continue

            # Validate all properties in the rules
            for rule_property, rules in rule_properties.items():

                if rules['Required']:
                    # Check if the property is specified
                    if rule_property not in resource_properties:
                        self.errors.append(
                            'Mandatory property "{}" not specified for {} ({}). See: {}'
                            .format(rule_property, resource_name, resource['Type'], rules['Documentation'])
                        )
                        continue

                if rule_property in resource_properties:
                    property_value = resource_properties[rule_property]

                    # Check if it has is a valid value
                    if rules:
                        if 'AllowedValues' in rules:
                            if rules['AllowedValues']:
                                if property_value not in rules['AllowedValues']:
                                    self.errors.append(
                                        'Invalid property value "{}" specified for {}.{} See: {}'
                                        .format(property_value, resource_name, rule_property, rules['Documentation'])
                                    )
                                    continue
