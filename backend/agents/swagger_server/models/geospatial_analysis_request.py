# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.geospatial_analysis_request_time_range import GeospatialAnalysisRequestTimeRange  # noqa: F401,E501
from swagger_server import util


class GeospatialAnalysisRequest(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, region: str=None, time_range: GeospatialAnalysisRequestTimeRange=None):  # noqa: E501
        """GeospatialAnalysisRequest - a model defined in Swagger

        :param region: The region of this GeospatialAnalysisRequest.  # noqa: E501
        :type region: str
        :param time_range: The time_range of this GeospatialAnalysisRequest.  # noqa: E501
        :type time_range: GeospatialAnalysisRequestTimeRange
        """
        self.swagger_types = {
            'region': str,
            'time_range': GeospatialAnalysisRequestTimeRange
        }

        self.attribute_map = {
            'region': 'region',
            'time_range': 'time_range'
        }
        self._region = region
        self._time_range = time_range

    @classmethod
    def from_dict(cls, dikt) -> 'GeospatialAnalysisRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeospatialAnalysisRequest of this GeospatialAnalysisRequest.  # noqa: E501
        :rtype: GeospatialAnalysisRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def region(self) -> str:
        """Gets the region of this GeospatialAnalysisRequest.

        Target region for geospatial analysis.  # noqa: E501

        :return: The region of this GeospatialAnalysisRequest.
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region: str):
        """Sets the region of this GeospatialAnalysisRequest.

        Target region for geospatial analysis.  # noqa: E501

        :param region: The region of this GeospatialAnalysisRequest.
        :type region: str
        """

        self._region = region

    @property
    def time_range(self) -> GeospatialAnalysisRequestTimeRange:
        """Gets the time_range of this GeospatialAnalysisRequest.


        :return: The time_range of this GeospatialAnalysisRequest.
        :rtype: GeospatialAnalysisRequestTimeRange
        """
        return self._time_range

    @time_range.setter
    def time_range(self, time_range: GeospatialAnalysisRequestTimeRange):
        """Sets the time_range of this GeospatialAnalysisRequest.


        :param time_range: The time_range of this GeospatialAnalysisRequest.
        :type time_range: GeospatialAnalysisRequestTimeRange
        """

        self._time_range = time_range
