# coding: utf-8

from __future__ import absolute_import
from typing import List, Dict, Any

class DataManagementTransformRequest:
    """Model for Data Management Transform Request."""

    def __init__(self, dataset_url: str, transformation_type: str, parameters: Dict[str, Any] = None):
        """
        DataManagementTransformRequest - a model defined for data transformation requests.

        :param dataset_url: The URL of the dataset to be transformed.
        :type dataset_url: str
        :param transformation_type: The type of transformation to be applied.
        :type transformation_type: str
        :param parameters: Additional parameters for the transformation.
        :type parameters: Dict[str, Any]
        """
        self.dataset_url = dataset_url
        self.transformation_type = transformation_type
        self.parameters = parameters if parameters is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        """Converts the model instance to a dictionary.

        :return: A dictionary representation of the model.
        :rtype: Dict[str, Any]
        """
        return {
            'dataset_url': self.dataset_url,
            'transformation_type': self.transformation_type,
            'parameters': self.parameters
        }
