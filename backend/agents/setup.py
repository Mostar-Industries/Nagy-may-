# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="MNTRK by MoStar Industries AI Agent API",
    author_email="akanimo@57vflx.onmicrosoft.com",
    url="",
    keywords=["Swagger", "MNTRK by MoStar Industries AI Agent API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    This API provides robust and accurate tools for tracking Mastomys Natalensis populations, analyzing ecological trends, and supporting Lassa fever outbreak management in Nigeria. Designed with a focus on real-time data, environmental analysis, and outbreak hotspots. This is the API for the AI agent, providing direct interaction with the AI system. 
    """
)
