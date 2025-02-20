from ..tokenizers.gpt2_tokenzier import GPT2Tokenizer


class TokenHandling:
    """Mixin class for token counting."""
   
    def _get_num_tokens_by_gpt2(self, text: str) -> int:
        """
        Calculate token count using GPT2 tokenizer.
        Since some model providers don't offer interfaces for token counting,
        we use GPT2 tokenizer for calculation.
        This method can be executed offline, with GPT2 tokenizer cached in the project.

        :param text: Plain text of the prompt. Original message needs to be converted to plain text
        :return: Number of tokens
        """
        return GPT2Tokenizer.get_num_tokens(text)
