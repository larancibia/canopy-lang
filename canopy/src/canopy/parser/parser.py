"""Parser for Canopy trading language"""

from pathlib import Path
from typing import Dict, List, Any
import re
from canopy.domain.strategy import Strategy, MACrossoverStrategy
from canopy.domain.indicator import SMA, EMA, RSI


def parse_strategy_file(file_path: Path) -> Strategy:
    """
    Parse .canopy strategy file

    Args:
        file_path: Path to .canopy file

    Returns:
        Strategy instance

    Example:
        strategy "Name"
        
        fast_ma = sma(close, 50)
        slow_ma = sma(close, 200)
        
        buy when crossover(fast_ma, slow_ma)
        sell when crossunder(fast_ma, slow_ma)
        
        plot(fast_ma, "Fast MA", color=blue)
    """
    with open(file_path) as f:
        code = f.read()

    return parse_strategy(code)


def parse_strategy(code: str) -> Strategy:
    """
    Parse strategy code

    Args:
        code: Canopy language code

    Returns:
        Strategy instance

    Raises:
        ValueError: If syntax is invalid
    """
    lines = code.strip().split("\n")

    strategy_name = None
    indicators: Dict[str, Any] = {}
    buy_rules: List[str] = []
    sell_rules: List[str] = []
    plots: List[str] = []

    for line in lines:
        # Strip whitespace and inline comments
        line = line.split("#")[0].strip()

        # Skip empty lines
        if not line:
            continue

        # Parse strategy name
        if line.startswith("strategy"):
            match = re.match(r'strategy\s+"([^"]+)"', line)
            if match:
                strategy_name = match.group(1)

        # Parse indicator definitions (variable = function(...))
        elif "=" in line and "when" not in line:
            var_name, expr = line.split("=", 1)
            var_name = var_name.strip()
            expr = expr.strip()

            # Parse SMA
            if expr.startswith("sma("):
                match = re.match(r"sma\((\w+),\s*(\d+)\)", expr)
                if match:
                    source = match.group(1)  # e.g., "close"
                    period = int(match.group(2))
                    indicators[var_name] = SMA(period=period)

            # Parse EMA
            elif expr.startswith("ema("):
                match = re.match(r"ema\((\w+),\s*(\d+)\)", expr)
                if match:
                    source = match.group(1)
                    period = int(match.group(2))
                    indicators[var_name] = EMA(period=period)

            # Parse RSI
            elif expr.startswith("rsi("):
                match = re.match(r"rsi\((\w+)(?:,\s*(\d+))?\)", expr)
                if match:
                    period = int(match.group(2)) if match.group(2) else 14
                    indicators[var_name] = RSI(period=period)

        # Parse buy rules
        elif line.startswith("buy when"):
            condition = line.replace("buy when", "").strip()
            buy_rules.append(condition)

        # Parse sell rules
        elif line.startswith("sell when"):
            condition = line.replace("sell when", "").strip()
            sell_rules.append(condition)

        # Parse plot commands
        elif line.startswith("plot("):
            # For MVP, just store the plot info (not used yet)
            plots.append(line)

    if not strategy_name:
        raise ValueError("Strategy must have a name: strategy \"Name\"")

    # For MVP, create a simple MA crossover strategy
    # In full version, this would compile to executable code
    strategy = create_ma_crossover_strategy(
        name=strategy_name,
        indicators=indicators,
        buy_rules=buy_rules,
        sell_rules=sell_rules,
    )

    return strategy


def create_ma_crossover_strategy(
    name: str,
    indicators: Dict[str, Any],
    buy_rules: List[str],
    sell_rules: List[str],
) -> Strategy:
    """
    Create MA crossover strategy instance

    For MVP, this is hardcoded to create MACrossoverStrategy.
    In full version, this would be dynamic based on parsed rules.

    Args:
        name: Strategy name
        indicators: Dictionary of indicator definitions
        buy_rules: List of buy conditions
        sell_rules: List of sell conditions

    Returns:
        Strategy instance

    Raises:
        ValueError: If required indicators are missing
    """
    # Extract fast and slow MA from indicators
    # This is simplified for MVP
    fast_ma = None
    slow_ma = None

    for var_name, indicator in indicators.items():
        # Look for indicators with "fast" or "slow" in name
        if "fast" in var_name.lower():
            fast_ma = indicator
        elif "slow" in var_name.lower():
            slow_ma = indicator

    if not fast_ma or not slow_ma:
        raise ValueError("MA crossover strategy requires fast_ma and slow_ma indicators")

    return MACrossoverStrategy(
        name=name,
        fast_period=fast_ma.period,
        slow_period=slow_ma.period,
    )
