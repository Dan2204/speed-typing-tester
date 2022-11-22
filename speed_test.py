import random
from typing import Union
from words import words

DEFAULT_WORDS = 20


class SpeedTest:

    def __init__(self, num_words: int = DEFAULT_WORDS):
        self.num_words = num_words
        self._get_words(num_words)
        self._current_index = 0
        self.current_word = self.words[self._current_index]

    def _get_words(self, size: int) -> None:
        self.words = set()
        while len(self.words) < size:
            self.words.add(random.choice(words))
        self.words = list(self.words)

    def get_next_word(self) -> Union[str, None]:
        self._current_index += 1
        if self._current_index >= len(self.words):
            return None
        self.current_word = self.words[self._current_index]
        return self.current_word

    def get_all_words(self) -> str:
        for word in self.words:
            yield word

    def reset_words(self):
        self._get_words(self.num_words)
        self._current_index = 0
        self.current_word = self.words[self._current_index]
