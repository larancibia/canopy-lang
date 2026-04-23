"""
Data Provider Factory — stub for alpha release.

In v0.0.2 this module exists only so that CLI imports succeed.
Concrete adapters (Yahoo Finance, CSV) will ship in a later alpha.

Users who want to run backtests today should bring their own
`pandas.DataFrame` of OHLCV data and use the domain/application layer
directly. See README "Alpha" section for details.
"""
from __future__ import annotations

from typing import Any

from canopy.ports.data_provider import IDataProvider

_NOT_IMPLEMENTED_MSG = (
    "Data provider adapters are not implemented in this alpha release. "
    "Bring your own pandas.DataFrame of OHLCV and use the domain/application "
    "layer directly, or track progress at "
    "https://github.com/larancibia/canopy-lang/issues."
)


class DataProviderFactory:
    """Factory for data provider adapters.

    Alpha note
    ----------
    This factory is intentionally a stub in v0.0.2. Calling any of its
    methods raises NotImplementedError with a message explaining the
    current state. The class exists so that the CLI and other entry
    points can import it without breaking.
    """

    _PROVIDERS_NOTE = "yahoo, csv — not implemented yet"

    @classmethod
    def create(cls, provider: str, **_kwargs: Any) -> IDataProvider:
        """Create a data provider by name.

        Always raises NotImplementedError in this release.
        """
        raise NotImplementedError(
            f"{_NOT_IMPLEMENTED_MSG} "
            f"Requested provider: {provider!r}. "
            f"Available: {cls._PROVIDERS_NOTE}."
        )

    @classmethod
    def available_providers(cls) -> list[str]:
        """Return the (currently empty) list of implemented providers."""
        return []
