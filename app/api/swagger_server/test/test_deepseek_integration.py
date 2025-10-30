import unittest
from swagger_server.utils.deepseek_service import DeepSeekService
import os
import logging
from unittest.mock import patch, MagicMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDeepSeekIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests"""
        try:
            cls.deepseek = DeepSeekService()
            logger.info("DeepSeek service initialized for testing")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek service: {str(e)}")
            raise

    def setUp(self):
        """Set up test case"""
        self.test_prompt = "Test prompt for code analysis"
        self.test_model = "deepseek-coder"

    @patch('swagger_server.utils.deepseek_service.DeepSeekAPI')
    def test_process_prompt_success(self, mock_deepseek_api):
        """Test successful prompt processing"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.text = "Test response from DeepSeek"
        mock_client = MagicMock()
        mock_client.generate.return_value = mock_response
        mock_deepseek_api.return_value = mock_client

        result = self.deepseek.process_prompt(self.test_prompt, self.test_model)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "Test response from DeepSeek")
        mock_client.generate.assert_called_once_with(
            prompt=self.test_prompt,
            model=self.test_model,
            max_tokens=150,
            temperature=0.7
        )

    @patch('swagger_server.utils.deepseek_service.DeepSeekAPI')
    def test_process_prompt_api_error(self, mock_deepseek_api):
        """Test handling of API errors"""
        # Mock API error
        mock_client = MagicMock()
        mock_client.generate.side_effect = Exception("API Error")
        mock_deepseek_api.return_value = mock_client

        result = self.deepseek.process_prompt(self.test_prompt, self.test_model)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "API Error")

    def test_missing_api_key(self):
        """Test behavior with missing API key"""
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': ''}):
            service = DeepSeekService()
            result = service.process_prompt(self.test_prompt)
            
            self.assertFalse(result["success"])
            self.assertIn("API key", str(result["error"]).lower())

    @patch('swagger_server.utils.deepseek_service.DeepSeekAPI')
    def test_different_model_parameters(self, mock_deepseek_api):
        """Test processing with different model parameters"""
        test_cases = [
            {"model": "deepseek-coder-instruct", "prompt": "Write a function"},
            {"model": "deepseek-large", "prompt": "Analyze this code"},
        ]

        mock_response = MagicMock()
        mock_response.text = "Model-specific response"
        mock_client = MagicMock()
        mock_client.generate.return_value = mock_response
        mock_deepseek_api.return_value = mock_client

        for case in test_cases:
            with self.subTest(model=case["model"]):
                result = self.deepseek.process_prompt(case["prompt"], case["model"])
                
                self.assertTrue(result["success"])
                self.assertEqual(result["response"], "Model-specific response")
                mock_client.generate.assert_called_with(
                    prompt=case["prompt"],
                    model=case["model"],
                    max_tokens=150,
                    temperature=0.7
                )

    @patch('swagger_server.utils.deepseek_service.DeepSeekAPI')
    def test_concurrent_requests(self, mock_deepseek_api):
        """Test handling of concurrent requests"""
        import concurrent.futures

        mock_response = MagicMock()
        mock_response.text = "Concurrent response"
        mock_client = MagicMock()
        mock_client.generate.return_value = mock_response
        mock_deepseek_api.return_value = mock_client

        def make_request(prompt):
            return self.deepseek.process_prompt(prompt)

        prompts = [f"Concurrent prompt {i}" for i in range(5)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(make_request, prompts))
        
        for result in results:
            self.assertTrue(result["success"])
            self.assertEqual(result["response"], "Concurrent response")

    @patch('swagger_server.utils.deepseek_service.DeepSeekAPI')
    def test_error_recovery(self, mock_deepseek_api):
        """Test service recovery after errors"""
        # First call fails
        mock_client = MagicMock()
        mock_client.generate.side_effect = [
            Exception("Temporary error"),  # First call fails
            MagicMock(text="Recovery response")  # Second call succeeds
        ]
        mock_deepseek_api.return_value = mock_client

        # First request - should fail
        result1 = self.deepseek.process_prompt(self.test_prompt)
        self.assertFalse(result1["success"])
        self.assertEqual(result1["error"], "Temporary error")

        # Second request - should succeed
        result2 = self.deepseek.process_prompt(self.test_prompt)
        self.assertTrue(result2["success"])
        self.assertEqual(result2["response"], "Recovery response")

if __name__ == '__main__':
    unittest.main()
