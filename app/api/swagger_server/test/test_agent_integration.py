import unittest
from flask import json
from swagger_server.utils.deepseek_service import DeepSeekService
from swagger_server.__main__ import app
import logging
from unittest.mock import patch, MagicMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAgentIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests"""
        try:
            cls.deepseek = DeepSeekService()
            cls.client = app.test_client()
            logger.info("Test client and DeepSeek service initialized")
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            raise

    def setUp(self):
        """Set up test case"""
        self.headers = {
            'Content-Type': 'application/json'
        }

    def test_gpt3_endpoint(self):
        """Test POST /gpt3 endpoint"""
        test_request = {
            "prompt": "Test prompt for GPT-3",
            "max_tokens": 100
        }

        response = self.client.post('/gpt3',
                                  data=json.dumps(test_request),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)

    def test_deepseek_endpoint(self):
        """Test POST /deepseek endpoint"""
        test_request = {
            "prompt": "Test prompt for code analysis",
            "model": "deepseek-coder"
        }

        response = self.client.post('/deepseek',
                                  data=json.dumps(test_request),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('response', data)

    def test_habitat_analysis_endpoint(self):
        """Test POST /ai/habitats endpoint"""
        test_request = {
            "location": {
                "latitude": 45.0,
                "longitude": -75.0
            },
            "environmental_data": {
                "temperature": 25,
                "humidity": 70,
                "rainfall": 100
            },
            "analysis_parameters": {
                "timeframe": "monthly",
                "resolution": "high"
            }
        }

        response = self.client.post('/ai/habitats',
                                  data=json.dumps(test_request),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('predictions', data)

    def test_risk_analysis_endpoint(self):
        """Test POST /ai/forecast/risk-analysis endpoint"""
        test_request = {
            "region": "test_region",
            "timeframe": "1_month",
            "environmental_factors": {
                "temperature_range": [20, 30],
                "humidity_range": [60, 80],
                "rainfall": 150
            }
        }

        response = self.client.post('/ai/forecast/risk-analysis',
                                  data=json.dumps(test_request),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('risk_level', data)
        self.assertIn('factors', data)

    def test_rag_query_endpoint(self):
        """Test POST /ai/rag-query endpoint"""
        test_request = {
            "query": "Test query about Mastomys habitat",
            "context": {
                "location": "test_location",
                "timeframe": "current"
            }
        }

        response = self.client.post('/ai/rag-query',
                                  data=json.dumps(test_request),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('sources', data)

    @patch('swagger_server.utils.deepseek_service.DeepSeekAPI')
    def test_model_error_handling(self, mock_deepseek_api):
        """Test handling of model errors"""
        # Mock API error
        mock_client = MagicMock()
        mock_client.generate.side_effect = Exception("Model error")
        mock_deepseek_api.return_value = mock_client

        test_request = {
            "prompt": "Test prompt",
            "model": "deepseek-coder"
        }

        response = self.client.post('/deepseek',
                                  data=json.dumps(test_request),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)

    def test_invalid_requests(self):
        """Test handling of invalid requests"""
        # Test missing prompt
        response = self.client.post('/deepseek',
                                  data=json.dumps({}),
                                  headers=self.headers)
        self.assertEqual(response.status_code, 400)

        # Test invalid JSON
        response = self.client.post('/deepseek',
                                  data="invalid json",
                                  headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_concurrent_model_requests(self):
        """Test handling of concurrent model requests"""
        import concurrent.futures

        test_request = {
            "prompt": "Test prompt for concurrent processing",
            "model": "deepseek-coder"
        }

        def make_request():
            return self.client.post('/deepseek',
                                  data=json.dumps(test_request),
                                  headers=self.headers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]

        for response in responses:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data.get('success'))
            self.assertIn('response', data)

    def test_model_response_validation(self):
        """Test validation of model responses"""
        test_cases = [
            {
                "endpoint": "/deepseek",
                "request": {
                    "prompt": "Test prompt 1",
                    "model": "deepseek-coder"
                }
            },
            {
                "endpoint": "/gpt3",
                "request": {
                    "prompt": "Test prompt 2",
                    "max_tokens": 100
                }
            }
        ]

        for case in test_cases:
            with self.subTest(endpoint=case["endpoint"]):
                response = self.client.post(case["endpoint"],
                                          data=json.dumps(case["request"]),
                                          headers=self.headers)
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                if case["endpoint"] == "/deepseek":
                    self.assertTrue(data.get('success'))
                self.assertIn('response', data)
                self.assertIsInstance(data['response'], str)

if __name__ == '__main__':
    unittest.main()
