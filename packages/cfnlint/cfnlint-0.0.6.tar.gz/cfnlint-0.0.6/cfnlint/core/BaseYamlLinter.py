import os
import yaml
from abc import ABCMeta, abstractmethod

class BaseYamlLinter(metaclass=ABCMeta):

    def __init__(self, file_path, lintingrules=None):

        if not os.path.isfile(file_path):
            raise ValueError("The file '%s' does not exist" % file_path)

        # Global issues
        self.errors = []

        self.file_path = file_path
        self.lintingrules = lintingrules

        self.file_as_yaml = self.__load_yaml_file(file_path)

    def __load_yaml_file(self, file_path):
        with open(file_path) as stream:
            file_contents = stream.read()

        file_contents_yaml = yaml.load(file_contents)

        # Validate the YAML
        self.__validate_valid_yaml(file_path, file_contents_yaml)

        return file_contents_yaml

    def __validate_valid_yaml(self, file_path, file_contents_yaml):
        if file_contents_yaml is None:
            raise ValueError("The file '%s' is empty" % file_path)

        if file_contents_yaml.get('Resources') is None:
            raise ValueError("Mandatory property 'Resources' is missing in file '%s'" % file_path)

    @abstractmethod
    def lint(self):
        """
        Lints the specified yaml file
        """
        pass
