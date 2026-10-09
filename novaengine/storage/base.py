"""Abstract persistence contract for portfolio and transaction state."""

from abc import ABC, abstractmethod
from typing import Optional
from novaengine.core.portfolio import PortfolioState


class StorageProvider(ABC):
    """Base interface for persisting engine state between runs."""

    @abstractmethod
    def save(self, state: PortfolioState) -> bool:
        """Persists the full portfolio state to storage."""

    @abstractmethod
    def load(self) -> Optional[PortfolioState]:
        """Loads and reconstructs the portfolio state from storage."""
