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
    description="MNTRK API by MoStar Industries",
    author_email="support@mo-overlord.tech",
    url="",
    keywords=["Swagger", "MNTRK API by MoStar Industries"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    This API provides robust tools for tracking Mastomys Natalensis populations, analyzing ecological trends, and supporting Lassa fever outbreak management. It is aligned with Nigeria CDC requirements and integrates with Supabase. 
    """
)
