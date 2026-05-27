from abc import ABC, abstractmethod

from .base import PlatformRule


class PlatformAdapter(ABC):
    rule: PlatformRule

    @abstractmethod
    def get_prompt_context(self) -> str:
        ...

    @abstractmethod
    def get_generation_prompt(self) -> str:
        ...

    @abstractmethod
    def get_title_prompt_extra(self) -> str:
        ...

    @abstractmethod
    def get_rhythm_prompt_extra(self) -> str:
        ...

    @abstractmethod
    def get_storyboard_prompt_extra(self) -> str:
        ...

    @abstractmethod
    def get_hashtag_prompt_extra(self) -> str:
        ...