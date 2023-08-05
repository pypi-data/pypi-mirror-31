from setuptools import setup, find_packages

setup(name='cfnlint',
      version='0.0.3',
      description='AWS Cloudformation linter',
      long_description='',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
      ],
      keywords='AWS CloudFormation Linter yaml json',
      url='http://github.com/fatbasstard/cfnlint',
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
