from abc import ABC, abstractmethod


class Bucket(ABC):

    @abstractmethod
    def save_file(self, filename: str, key: str):
        pass

    @abstractmethod
    def get_file(self, key: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, key: str):
        pass
