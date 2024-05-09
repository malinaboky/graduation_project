from typing import List


class ContentTypeChecker:
    def __init__(self, content_types: List[str]) -> None:
        self.content_types = content_types

    def __call__(self, content_type: str = ''):
        if content_type and content_type not in self.content_types:
            return False
        return True


class ContentLenChecker:
    def __init__(self, content_len: int) -> None:
        self.content_len = content_len

    def __call__(self, content_len: int = 0):
        return content_len <= self.content_len
