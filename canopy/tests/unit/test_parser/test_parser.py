"""Tests for Canopy language parser"""

import pytest
from pathlib import Path
from canopy.parser.parser import parse_strategy, parse_strategy_file
from canopy.domain.strategy import MACrossoverStrategy
from canopy.domain.indicator import SMA, EMA, RSI


def test_parser_parses_strategy_name():
    """Test that parser extracts strategy name"""
    code = '''strategy "My Test Strategy"

fast_ma = sma(close, 10)
slow_ma = sma(close, 20)
'''

    strategy = parse_strategy(code)

    assert strategy.name == "My Test Strategy"


def test_parser_parses_indicator_definitions():
    """Test that parser extracts indicator definitions"""
    code = '''strategy "Test"
    
fast_ma = sma(close, 50)
slow_ma = sma(close, 200)
rsi_14 = rsi(close, 14)
'''
    
    strategy = parse_strategy(code)
    assert strategy.name == "Test"
    # For MVP, we're creating a MACrossoverStrategy
    assert strategy.fast_period == 50
    assert strategy.slow_period == 200


def test_parser_parses_buy_sell_rules():
    """Test that parser extracts buy/sell rules"""
    code = '''strategy "Crossover"

fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)
'''
    
    strategy = parse_strategy(code)
    assert strategy.name == "Crossover"
    assert isinstance(strategy, MACrossoverStrategy)


def test_parser_parses_plot_commands():
    """Test that parser handles plot commands"""
    code = '''strategy "Visual Strategy"

fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
'''
    
    # Should not raise error
    strategy = parse_strategy(code)
    assert strategy.name == "Visual Strategy"


def test_parser_handles_comments():
    """Test that parser ignores comments"""
    code = '''# This is a comment
strategy "Commented Strategy"

# Define indicators
fast_ma = sma(close, 50)  # Fast moving average
slow_ma = sma(close, 200)  # Slow moving average

# Entry/exit rules
buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)
'''
    
    strategy = parse_strategy(code)
    assert strategy.name == "Commented Strategy"


def test_parser_raises_on_syntax_error():
    """Test that parser raises error on invalid syntax"""
    code = '''# Missing strategy name
fast_ma = sma(close, 50)
'''
    
    with pytest.raises(ValueError, match="Strategy must have a name"):
        parse_strategy(code)


def test_parser_parses_strategy_file(tmp_path):
    """Test that parser can read from file"""
    strategy_file = tmp_path / "test_strategy.canopy"
    strategy_file.write_text('''strategy "File Strategy"

fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)
''')
    
    strategy = parse_strategy_file(strategy_file)
    assert strategy.name == "File Strategy"
    assert strategy.fast_period == 50
    assert strategy.slow_period == 200


def test_parser_parses_ema_indicators():
    """Test that parser handles EMA indicators"""
    code = '''strategy "EMA Strategy"

fast_ema = ema(close, 12)
slow_ema = ema(close, 26)

buy when crossover(fast_ema, slow_ema)
sell when crossunder(fast_ema, slow_ema)
'''
    
    strategy = parse_strategy(code)
    assert strategy.name == "EMA Strategy"
