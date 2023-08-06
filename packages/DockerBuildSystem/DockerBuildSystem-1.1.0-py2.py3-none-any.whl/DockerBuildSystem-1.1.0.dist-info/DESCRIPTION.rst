# Docker Build System

A simple library for handling docker commands with python.
Please have a look at an example of use at the repository.

## Install And/Or Upgrade
- pip install --no-cache-dir --upgrade DockerBuildSystem

## Prerequisites
- Docker:
    - https://www.docker.com/get-docker

## Additional Info
- The pip package may be located at:
    - https://pypi.org/project/DockerBuildSystem

## Publish New Version.
1. Configure setup.py with new version.
2. Build: python setup.py bdist_wheel
3. Publish: twine upload dist/*

