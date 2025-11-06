"""CLI - Command-line interface for Canopy"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from canopy import __version__
from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.domain.metrics import PerformanceMetrics
from canopy.parser.parser import parse_strategy_file
from canopy.domain.backtest import Backtest

app = typer.Typer(help="Canopy - Modern Trading Language")
console = Console()

# Strategy template for new strategies
STRATEGY_TEMPLATE = '''strategy "My Strategy"

# Define indicators
fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

# Define entry/exit rules
buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

# Plotting
plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
'''


@app.command()
def version() -> None:
    """Show Canopy version"""
    console.print(f"Canopy version {__version__}", style="bold green")


@app.command()
def new(
    name: str,
    directory: str = ".",
) -> None:
    """
    Create a new strategy

    Args:
        name: Strategy name
        directory: Directory to create strategy in
    """
    # Create strategy directory
    dir_path = Path(directory)
    strategy_dir = dir_path / name
    strategy_dir.mkdir(exist_ok=True)

    # Create strategy.canopy file with template
    strategy_file = strategy_dir / "strategy.canopy"
    strategy_file.write_text(STRATEGY_TEMPLATE)

    console.print(f"✅ Created strategy: {strategy_dir}", style="bold green")
    console.print(f"Edit {strategy_file} to customize your strategy")


@app.command()
def backtest(
    strategy_file: str,
    symbol: str = "SPY",
    start: str = "2020-01-01",
    end: str = "2024-12-31",
    capital: float = 10000.0,
    provider: str = "yahoo",
) -> None:
    """
    Run a backtest

    Args:
        strategy_file: Path to .canopy strategy file
        symbol: Ticker symbol
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        capital: Initial capital
        provider: Data provider (yahoo or csv)
    """
    try:
        # 1. Parse strategy
        strategy_path = Path(strategy_file)
        console.print(f"📖 Parsing strategy: {strategy_path}", style="blue")
        strategy = parse_strategy_file(strategy_path)

        # 2. Fetch data
        console.print(f"📊 Fetching data for {symbol}...", style="blue")
        data_provider = DataProviderFactory.create(provider)
        timeseries = data_provider.get_ohlcv(symbol, start, end)

        # 3. Setup backtest engine and use case
        backtest_engine = SimpleBacktestEngine()
        use_case = RunBacktestUseCase(backtest_engine)

        # 4. Run backtest
        console.print(f"🔄 Running backtest...", style="blue")
        backtest_result, metrics = use_case.execute(
            strategy=strategy,
            timeseries=timeseries,
            initial_capital=capital,
        )

        # 5. Display results
        display_results(strategy.name, backtest_result, metrics)

    except FileNotFoundError as e:
        console.print(f"❌ Error: File not found - {strategy_file}", style="bold red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        raise typer.Exit(1)


def display_results(
    strategy_name: str, backtest: Backtest, metrics: PerformanceMetrics
) -> None:
    """Display backtest results in beautiful table"""
    console.print(f"\n✅ Backtest Complete: {strategy_name}\n", style="bold green")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Return", f"{metrics.total_return:.2f}%")
    table.add_row("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}")
    table.add_row("Sortino Ratio", f"{metrics.sortino_ratio:.2f}")
    table.add_row("Max Drawdown", f"{metrics.max_drawdown:.2f}%")
    table.add_row("Win Rate", f"{metrics.win_rate:.2f}%")
    table.add_row("Profit Factor", f"{metrics.profit_factor:.2f}")
    table.add_row("Total Trades", str(metrics.total_trades))
    table.add_row("Winning Trades", str(metrics.winning_trades))
    table.add_row("Losing Trades", str(metrics.losing_trades))

    console.print(table)


def main() -> None:
    """Entry point for CLI"""
    app()


if __name__ == "__main__":
    main()
