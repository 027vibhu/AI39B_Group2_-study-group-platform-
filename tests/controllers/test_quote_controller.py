"""Unit tests for QuoteController (static list, no DB)."""

import unittest

from app.controllers.quote_controller import QuoteController, QUOTES


class TestQuoteController(unittest.TestCase):
    def setUp(self):
        self.controller = QuoteController()

    def test_returns_a_known_quote(self):
        quote = self.controller.get_random_quote()
        self.assertIsInstance(quote, str)
        self.assertIn(quote, QUOTES)


if __name__ == '__main__':
    unittest.main()
