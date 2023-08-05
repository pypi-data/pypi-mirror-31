from cfnlint.linter import linter
import click

@click.command()
@click.option('--cfn_file', default='test_stack.yaml', help='The CLoudFormation (yaml) file to lint')
@click.option('--aws_region', default='eu-west-1', help='The AWS region')
def main(cfn_file, aws_region):
    print('cfn-lint: AWS CloudFormation Linter`')
    print('Linting {}'.format(cfn_file))

    errors = linter(cfn_file)
    print('\n'.join(errors))
