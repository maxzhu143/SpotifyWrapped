import unittest
from unittest.mock import MagicMock, patch
from Wrappedapp.openai_functions import generate_psychoanalysis

class OpenAIFunctionsTestCase(unittest.TestCase):

    @patch('Wrappedapp.openai_functions.client.chat.completions.create')
    def test_generate_psychoanalysis(self, mock_openai_completion):
        # Mocking the OpenAI API response
        mock_openai_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="listener type some text"))]
        )

        # Import the function to be tested
        from Wrappedapp.openai_functions import generate_psychoanalysis

        # Call the function with test data
        result, word = generate_psychoanalysis(
            [{"name": "Song1"}], ["Artist1"], ["Genre1"], 100
        )

        # Validate the response
        self.assertEqual(word, "listener type")  # Validate the one-word description
        self.assertEqual(result, "some text")    # Validate the remaining text
