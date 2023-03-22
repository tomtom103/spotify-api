import random
import string


class RandomStringGenerator:
    def __init__(self, n: int) -> None:
        self.n = n

    def __call__(self) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=self.n))
