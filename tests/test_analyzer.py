import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from utils.analyzer import FeedAnalyzer

class TestFeedAnalyzer(unittest.IsolatedAsyncioTestCase):
    @patch("utils.analyzer.AsyncOpenAI")
    async def test_is_relevant_true(self, mock_openai_class):
        # Setup mock client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"relevant": true}'
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Test
        analyzer = FeedAnalyzer(api_key="fake_key")
        result = await analyzer.is_relevant("Test Title", "Test Summary", "Test Criteria")

        self.assertTrue(result)
        mock_client.chat.completions.create.assert_called_once()

    @patch("utils.analyzer.AsyncOpenAI")
    async def test_is_relevant_false(self, mock_openai_class):
        # Setup mock client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"relevant": false}'
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Test
        analyzer = FeedAnalyzer(api_key="fake_key")
        result = await analyzer.is_relevant("Another Title", "Another Summary", "Math")

        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()