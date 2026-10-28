from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def generate_explanation(self, payload: dict) -> str:
        """
        Generates a human-readable explanation based on the risk analysis payload.
        """
        pass
