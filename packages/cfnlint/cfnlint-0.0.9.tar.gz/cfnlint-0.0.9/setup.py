from setuptools import setup, find_packages

# Custom readme file for pypi
def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='cfnlint',
      version='0.0.9',
      description='AWS Cloudformation linter',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
      ],
      keywords='AWS CloudFormation Linter yaml json',
      url='http://github.com/fatbasstard/cfnlinter',
      author='Frank van Boven',
      author_email='frank@cenotaph.nl',
      license='GNU GPL 2.0',
      packages=find_packages(exclude=['tests*']),
      python_requires='>=3',
      install_requires=[
          'click',
          'pyyaml',
          'requests'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points={
          'console_scripts': ['cfn-lint=cfnlint.cli.cli:main'],
      },
      include_package_data=True,
      zip_safe=False)
