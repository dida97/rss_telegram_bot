import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from bot.handlers import (
    URL, NAME, CRITERIA, CONFIRMATION,
    start, add_source_start, add_source_url, add_source_name, add_source_criteria, cancel
)

class TestBotHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_add_source_start(self):
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        result = await add_source_start(update, context)

        self.assertEqual(result, URL)
        update.message.reply_text.assert_called_once()
        self.assertIn("What is the RSS feed URL?", update.message.reply_text.call_args[0][0])

    async def test_add_source_url(self):
        update = MagicMock()
        update.message.text = "http://example.com/rss"
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.user_data = {}

        result = await add_source_url(update, context)

        self.assertEqual(result, NAME)
        self.assertEqual(context.user_data['url'], "http://example.com/rss")
        update.message.reply_text.assert_called_once()
        self.assertIn("what should we name this source?", update.message.reply_text.call_args[0][0])

    async def test_add_source_name(self):
        update = MagicMock()
        update.message.text = "Tech News"
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.user_data = {}

        result = await add_source_name(update, context)

        self.assertEqual(result, CRITERIA)
        self.assertEqual(context.user_data['name'], "Tech News")
        update.message.reply_text.assert_called_once()
        self.assertIn("what are the criteria or topics of interest", update.message.reply_text.call_args[0][0])

    async def test_add_source_criteria(self):
        update = MagicMock()
        update.message.text = "AI agents"
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.user_data = {
            'url': "http://example.com/rss",
            'name': "Tech News"
        }

        result = await add_source_criteria(update, context)

        self.assertEqual(result, CONFIRMATION)
        self.assertEqual(context.user_data['criteria'], "AI agents")
        update.message.reply_text.assert_called_once()
        self.assertIn("Please confirm the new source details", update.message.reply_text.call_args[0][0])

if __name__ == "__main__":
    unittest.main()
