# Changelog

All notable changes to `canopy-lang` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- CSV data provider adapter
- Yahoo Finance data provider adapter
- Full CLI integration with data providers
- Documentation site

## [0.0.3] - 2026-04-23

### Fixed
- **Missing module in wheel**: v0.0.2 wheel did not include `canopy/adapters/data/` because a stray `.gitignore` rule excluded it. Files now force-added and shipped in the distribution.
- **v0.0.1 and v0.0.2 have been yanked from PyPI** — please use `pip install canopy-lang>=0.0.3`.

## [0.0.2] - 2026-04-23

### Fixed
- **CLI import error**: `canopy --help` failed with `ModuleNotFoundError: canopy.adapters.data`. Added stub `DataProviderFactory` so CLI imports succeed; it raises a clear `NotImplementedError` with guidance when data providers are requested.
- **Typer/Click incompatibility**: bumped `typer` dep from `^0.9.0` to `^0.12` to fix `Parameter.make_metavar()` error on recent Click versions.
- **Version mismatch**: `canopy version` now reports the real package version (was hardcoded to 0.1.0 while package was 0.0.1).

### Notes
- Data provider adapters (Yahoo Finance, CSV) still not implemented. The stub raises a `NotImplementedError` pointing to the issue tracker.
- **v0.0.1 has been yanked from PyPI** — please use `pip install canopy-lang>=0.0.2`.

## [0.0.1] - 2026-04-21

### Added
- Initial alpha release of Canopy DSL for trading strategy development
- Core DSL parser (strategy name, indicator definitions, buy/sell rules, plot commands, comments)
- Backtest engine with walk-forward optimization support
- Built-in technical indicators: SMA, EMA, RSI (more planned)
- Portfolio backtesting (multi-asset)
- Optimizers: Bayesian, Genetic Algorithm, Grid Search
- Performance metrics: Sharpe ratio, Sortino ratio, maximum drawdown, Monte Carlo, robustness
- Hexagonal architecture (domain / application / adapters / ports)
- CLI entry point via Typer (`canopy` command)
- Optional web backend (FastAPI) — install with `pip install canopy-lang[web]`
- 264 unit tests passing (parser, domain, application, adapters/optimization)

### Known Limitations
- **Data provider adapters not implemented yet**: `YahooFinanceProvider` and `CSVProvider` exist only as port interfaces. Users must bring their own `pandas.DataFrame` of OHLC data to run backtests.
- REST API and web frontend are experimental and not installed by default.

### Notes
- Alpha release — API may change before 1.0.
- Web dependencies (fastapi, uvicorn, httpx, python-multipart) are moved to optional `[web]` extras to keep core installs lightweight.
