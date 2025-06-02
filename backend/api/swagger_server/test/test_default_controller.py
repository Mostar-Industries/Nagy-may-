# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.adaptive_learning_request import AdaptiveLearningRequest  # noqa: E501
from swagger_server.models.adaptive_learning_response import AdaptiveLearningResponse  # noqa: E501
from swagger_server.models.anomaly_detection_request import AnomalyDetectionRequest  # noqa: E501
from swagger_server.models.anomaly_detection_response import AnomalyDetectionResponse  # noqa: E501
from swagger_server.models.api_temporalanalysis_body import ApiTemporalanalysisBody  # noqa: E501
from swagger_server.models.cluster_analysis_result import ClusterAnalysisResult  # noqa: E501
from swagger_server.models.data_transformation_request import DataTransformationRequest  # noqa: E501
from swagger_server.models.data_transformation_response import DataTransformationResponse  # noqa: E501
from swagger_server.models.detection_pattern import DetectionPattern  # noqa: E501
from swagger_server.models.detection_pattern_response import DetectionPatternResponse  # noqa: E501
from swagger_server.models.google_vision_request import GoogleVisionRequest  # noqa: E501
from swagger_server.models.google_vision_response import GoogleVisionResponse  # noqa: E501
from swagger_server.models.habitat_analysis_request import HabitatAnalysisRequest  # noqa: E501
from swagger_server.models.habitat_analysis_response import HabitatAnalysisResponse  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.lang_chain_request import LangChainRequest  # noqa: E501
from swagger_server.models.lang_chain_response import LangChainResponse  # noqa: E501
from swagger_server.models.movement_prediction_response import MovementPredictionResponse  # noqa: E501
from swagger_server.models.notification_subscription import NotificationSubscription  # noqa: E501
from swagger_server.models.notifications_subscribe_body import NotificationsSubscribeBody  # noqa: E501
from swagger_server.models.postgres_query_request import PostgresQueryRequest  # noqa: E501
from swagger_server.models.postgres_query_response import PostgresQueryResponse  # noqa: E501
from swagger_server.models.predictive_model_request import PredictiveModelRequest  # noqa: E501
from swagger_server.models.predictive_model_response import PredictiveModelResponse  # noqa: E501
from swagger_server.models.remote_sensing_augmentation_request import RemoteSensingAugmentationRequest  # noqa: E501
from swagger_server.models.remote_sensing_augmentation_response import RemoteSensingAugmentationResponse  # noqa: E501
from swagger_server.models.spatial_clustering_body import SpatialClusteringBody  # noqa: E501
from swagger_server.models.supabase_query_request import SupabaseQueryRequest  # noqa: E501
from swagger_server.models.supabase_query_response import SupabaseQueryResponse  # noqa: E501
from swagger_server.models.vision_analyze_request import VisionAnalyzeRequest  # noqa: E501
from swagger_server.models.vision_analyze_response import VisionAnalyzeResponse  # noqa: E501
from swagger_server.models.weather_climate_data import WeatherClimateData  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_analyze_habitats(self):
        """Test case for analyze_habitats

        Analyze satellite or environmental data for Mastomys Natalensis habitats
        """
        body = HabitatAnalysisRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/habitats',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_analyze_spatial_clustering(self):
        """Test case for analyze_spatial_clustering

        Analyze spatial clustering of detection patterns
        """
        body = SpatialClusteringBody()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/spatial/clustering',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_analyze_temporal_patterns(self):
        """Test case for analyze_temporal_patterns

        Analyze temporal patterns in detection data
        """
        body = ApiTemporalanalysisBody()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/temporal-analysis',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_analyze_vision(self):
        """Test case for analyze_vision

        Analyze images for Mastomys Natalensis
        """
        body = VisionAnalyzeRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/vision/analyze',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_apply_augmentation(self):
        """Test case for apply_augmentation

        Apply augmentation to remote sensing data
        """
        body = RemoteSensingAugmentationRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/augmentation/remote-sensing',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_configure_adaptive_learning(self):
        """Test case for configure_adaptive_learning

        Configure adaptive learning
        """
        body = AdaptiveLearningRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/adaptive-learning',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_detect_anomalies(self):
        """Test case for detect_anomalies

        Detect anomalies in data
        """
        body = AnomalyDetectionRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/anomaly-detection',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_generate_lang_chain_insights(self):
        """Test case for generate_lang_chain_insights

        Generate AI insights using LangChain with DeepSeek-R1-Distill-Qwen-7B
        """
        body = LangChainRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/langchain/generate',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_weather_climate_data(self):
        """Test case for get_weather_climate_data

        Retrieve weather and climate data for habitat analysis
        """
        query_string = [('latitude', 1.2),
                        ('longitude', 1.2),
                        ('timeframe', 'timeframe_example')]
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/integration/weather-climate',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_integrate_google_vision(self):
        """Test case for integrate_google_vision

        Integrate with Google Vision API
        """
        body = GoogleVisionRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/integration/vision/google-vision',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_predict_movements(self):
        """Test case for predict_movements

        Predict Mastomys movements
        """
        query_string = [('latitude', 1.2),
                        ('longitude', 1.2),
                        ('_date', '2013-10-20')]
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/predict-movements',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_predictive_modeling(self):
        """Test case for predictive_modeling

        Execute predictive modeling
        """
        body = PredictiveModelRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/modeling/predictive',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_query_postgres_data(self):
        """Test case for query_postgres_data

        Query data from Postgres database
        """
        body = PostgresQueryRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/integration/postgres/query',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_query_supabase_data(self):
        """Test case for query_supabase_data

        Query data from Supabase
        """
        body = SupabaseQueryRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/integration/supabase/query',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_record_detection_patterns(self):
        """Test case for record_detection_patterns

        Record detection patterns of Mastomys Natalensis
        """
        body = DetectionPattern()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/detection-patterns',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subscribe_to_notifications(self):
        """Test case for subscribe_to_notifications

        Subscribe to real-time notifications for detection events
        """
        body = NotificationsSubscribeBody()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/notifications/subscribe',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_transform_data(self):
        """Test case for transform_data

        Transform and clean datasets
        """
        body = DataTransformationRequest()
        response = self.client.open(
            '/marv-b24/MNTRK/1.0.1/api/data-transformation',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
