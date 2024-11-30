import unittest
from unittest.mock import patch
from Wrappedapp.openai_functions import generate_psychoanalysis

class OpenAIFunctionsTestCase(unittest.TestCase):
    @patch('Wrappedapp.openai_functions.client.chat.completions.create')
    def test_generate_psychoanalysis(self, mock_openai_completion):
        mock_openai_completion.return_value = MagicMock(choices=[{"message": {"content": "listener type some text"}}])
        result, word = generate_psychoanalysis(["Song1"], ["Artist1"], ["Genre1"], 100)
        self.assertIn("some text", result)
        self.assertIn("listener", word)
